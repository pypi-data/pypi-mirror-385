package signal

import (
	// Standard library.
	"context"
	"fmt"
	"time"

	// Third-party libraries.
	"github.com/google/uuid"
	"go.mau.fi/mautrix-signal/pkg/libsignalgo"
	"go.mau.fi/mautrix-signal/pkg/signalmeow"
	"go.mau.fi/mautrix-signal/pkg/signalmeow/events"
	signalpb "go.mau.fi/mautrix-signal/pkg/signalmeow/protobuf"
	"go.mau.fi/mautrix-signal/pkg/signalmeow/store"
)

const (
	// Enable backup capabilities.
	backupEnabled = true

	// Whether or not to synchronize contacts on login.
	alwaysSyncContacts = true

	// The initial provisioning state during login. This should be part of the original type, but is
	// (currently) not.
	stateProvisioningUnknown signalmeow.ProvisioningState = -1

	// How long before login process times out waiting for QR scan, and retries provisioning a new
	// QR code.
	loginTimeoutDuration = 45 * time.Second

	// Maximum number of times we'll attempt to fetch a new QR code when waiting for login.
	loginMaxRetries = 6
)

// A Session represents a connection to Signal under a given [Gateway]. In general, sessions are
// inactive until [Session.Login] is called and out-of-band registration is completed, in which case
// our internal event handlers will attempt to propagate any incoming events. Calls to session
// functions, such as [Session.GetContacts], will return an error immediately if the session is not
// active and  authenticated.
type Session struct {
	// Internal fields.
	gateway      *Gateway           // The [Gateway] this session is attached to.
	client       *signalmeow.Client // Concrete client connection to Signal for this [Session].
	device       LinkedDevice       // The linked device for this session.
	eventHandler HandleEventFunc    // The handler function to use for propagating events to the adapter.
}

// NewSession returns a new, inactive connection to Signal. Sessions are expected to be activated
// via subsequent calls to [Session.Login], which will generally continue out-of-band; see the
// relevant documentation for more details.
func NewSession(g *Gateway, d LinkedDevice) *Session {
	return &Session{gateway: g, device: d}
}

func (s *Session) Login() error {
	var ctx = context.Background()

	// Check for existing login for the device given.
	if s.device.ID != "" {
		aci, err := uuid.Parse(s.device.ID)
		if err != nil {
			return fmt.Errorf("failed to parse device ID as UUID: %s", err)
		}

		device, err := s.gateway.store.DeviceByACI(ctx, aci)
		if err != nil {
			return fmt.Errorf("failed to get device from store: %s", err)
		}

		if device != nil && device.IsDeviceLoggedIn() {
			return s.connect(ctx, device)
		}
	}

	go s.login(ctx)
	return nil
}

// Logout disconnects and unlinks the current active [Session]. If there is no active session, this
// function returns a nil error.
func (s *Session) Logout() error {
	// No active client presumably means nothing to log out of.
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return nil
	}

	var ctx = context.Background()
	if err := s.client.StopReceiveLoops(); err != nil {
		return fmt.Errorf("failed to stop connection")
	} else if err := s.client.Unlink(ctx); err != nil {
		return fmt.Errorf("failed to unlink device")
	} else if err := s.gateway.store.DeleteDevice(ctx, &s.client.Store.DeviceData); err != nil {
		return fmt.Errorf("failed to delete device from store")
	}

	s.client = nil
	return nil
}

// Disconnect stops any active connection to Signal without removing authentication credentials.
func (s *Session) Disconnect() error {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return fmt.Errorf("cannot disconnect for unauthenticated session")
	}

	return s.client.ClearKeysAndDisconnect(context.Background())
}

// The context key used for tracking login retries.
type loginCountKey struct{}

// Attach login count to given [context.Context] for use in subsequent calls.
func contextWithLoginCount(ctx context.Context, count int) context.Context {
	return context.WithValue(ctx, loginCountKey{}, count)
}

// Retrieve login count from given [context.Context], or return 0 if no existing count was found.
func loginCountFromContext(ctx context.Context) int {
	if count, ok := ctx.Value(loginCountKey{}).(int); ok {
		return count
	}
	return 0
}

// Process login, propagating events to the pre-set [HandleEventFunc] attached to the [Session].
// This function is expected to be run in a Goroutine, as it will otherwise block for an indefinite
// amount of time.
func (s *Session) login(ctx context.Context) {
	provCtx, provCancel := context.WithCancel(s.gateway.log.WithContext(ctx))
	ctx = contextWithLoginCount(ctx, loginCountFromContext(ctx)+1)

	var deviceID uuid.UUID
	prevState := stateProvisioningUnknown
	loginChan := signalmeow.PerformProvisioning(provCtx, s.gateway.store, s.gateway.Name, backupEnabled)

	for {
		select {
		// Handle incoming event from login channel. Typically, this will only handle a set of state
		// transitions, from provisioning URL, to device linking, to connection.
		case resp := <-loginChan:
			if resp.Err != nil {
				provCancel()
				s.gateway.log.Err(resp.Err).Msg("Failed getting response from login channel")
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
				return
			}
			switch {
			// Initial provisioning state: wait to receive provisioning URL (to transform to QR code).
			case resp.State == signalmeow.StateProvisioningURLReceived && prevState == stateProvisioningUnknown:
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{QRCode: resp.ProvisioningURL}})
			// QR code scanned: provision and link new device.
			case resp.State == signalmeow.StateProvisioningDataReceived && prevState == signalmeow.StateProvisioningURLReceived:
				if resp.ProvisioningData.ACI == uuid.Nil {
					provCancel()
					s.gateway.log.Error().Msg("No Signal account ID received in login")
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
					return
				} else if err := s.gateway.store.PutDevice(ctx, resp.ProvisioningData); err != nil {
					provCancel()
					s.gateway.log.Err(err).Msg("Failed storing device data")
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
					return
				}
				deviceID = resp.ProvisioningData.ACI
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{
					DeviceID: resp.ProvisioningData.ACI.String(),
				}})
			// Device keys received, connect to Signal with given credentials.
			case resp.State == signalmeow.StateProvisioningPreKeysRegistered && prevState == signalmeow.StateProvisioningDataReceived:
				provCancel()
				if deviceID == uuid.Nil {
					s.gateway.log.Error().Msg("No Signal account ID found in store")
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
					return
				}
				device, err := s.gateway.store.DeviceByACI(ctx, deviceID)
				if err != nil {
					s.gateway.log.Err(err).Msg("Failed fetching device from store")
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
				}
				if err := s.connect(ctx, device); err != nil {
					s.gateway.log.Err(err).Msg("Failed connecting after login")
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
				}
				return
			// Handle any errors encountered during provisioning.
			case resp.State == signalmeow.StateProvisioningError:
				provCancel()
				s.gateway.log.Err(resp.Err).Msg("Login failed with error")
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
				return
			// Fallback error handling for unhandled state transitions.
			default:
				provCancel()
				s.gateway.log.Error().Str("state", resp.State.String()).Str("prev", prevState.String()).Msg("Unexpected login state transition")
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: "Login failed for unknown reason"}})
				return
			}
			prevState = resp.State
		// We've been waiting for an event for some time; see if we're stuck at the initial provisioning
		// stage and retry login if so.
		case <-time.After(loginTimeoutDuration):
			if prevState == signalmeow.StateProvisioningURLReceived {
				provCancel()
				if loginCountFromContext(ctx) > loginMaxRetries {
					s.gateway.log.Error().Msg("Maximum number of login retries reached, stopping login")
				} else {
					s.login(ctx)
				}
				return
			}
		// Stop login process if parent context is closed.
		case <-ctx.Done():
			provCancel()
			if err := ctx.Err(); err != nil {
				s.gateway.log.Err(err).Msg("Error during login")
			}
			return
		}
	}
}

// Connect to Signal, initializing the internal client and handling any initial events for session
// bring-up. Calls to [Session.Logout] or [Session.Disconnect] will generally stop any ongoing
// processes initiated by this function.
func (s *Session) connect(ctx context.Context, device *store.Device) error {
	if s.client != nil && s.client.IsConnected() {
		return nil
	} else if s.client == nil {
		s.client = &signalmeow.Client{
			Store:                 device,
			Log:                   s.gateway.log,
			EventHandler:          s.handleClientEvent,
			SyncContactsOnConnect: alwaysSyncContacts,
		}
	}

	if err := s.client.RegisterCapabilities(ctx); err != nil {
		s.gateway.log.Err(err).Msg("Failed to register client capabilities")
	}

	connChan, err := s.client.StartReceiveLoops(ctx)
	if err != nil {
		// TODO: Implement retries?
		return fmt.Errorf("failed to start connection: %s", err)
	}

	// TODO: Implement sync chats?
	go func() {
		for {
			status, ok := <-connChan
			if !ok {
				s.gateway.log.Debug().Msg("Connection channel closed")
				return
			}

			switch status.Event {
			case signalmeow.SignalConnectionEventConnected:
				s.propagateEvent(EventConnect, &EventPayload{Connect: Connect{
					AccountID:   s.client.Store.ACI.String(),
					PhoneNumber: s.client.Store.Number,
				}})
			case signalmeow.SignalConnectionEventDisconnected:
				// TODO: These events can be transient, and we should probably not trigger reconnects immediately,
				// but we need to potentially recover.
				s.gateway.log.Warn().Msg("Received disconnection event")
			case signalmeow.SignalConnectionEventLoggedOut:
				// TODO: Disconnect from Signal.
				if err := s.Disconnect(); err != nil {
					s.gateway.log.Err(err).Msg("Failed to disconnect on logout event")
				}
				s.propagateEvent(EventLogout, nil)
			case signalmeow.SignalConnectionEventError:
				s.propagateEvent(EventConnect, &EventPayload{Connect: Connect{
					Error: status.Err.Error(),
				}})
			}
		}
	}()

	return nil
}

// SendMessage processes the given [Message], and sends it to to Signal. Messages can contain a
// multitude of different fields denoting different semantics, see the [Message] type for more
// information.
func (s *Session) SendMessage(message Message) (string, error) {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return "", fmt.Errorf("cannot send message for unauthenticated session")
	}

	recipientID, err := uuid.Parse(message.ChatID)
	if err != nil {
		return "", fmt.Errorf("failed parsing '%s' as UUID", message.ChatID)
	}

	var content = &signalpb.Content{}
	var messageTimestamp = makeMessageTimestamp()

	switch message.Kind {
	case MessagePlain:
		content.DataMessage = &signalpb.DataMessage{
			Timestamp: &messageTimestamp,
			Body:      &message.Body,
		}
		if message.ReplyTo.ID != "" {
			replyAuthor, replyTimestamp := parseMessageID(message.ReplyTo.ID)
			content.DataMessage.Quote = &signalpb.DataMessage_Quote{
				Id:        &replyTimestamp,
				AuthorAci: ptrTo(replyAuthor.String()),
				Text:      &message.ReplyTo.Body,
				Type:      signalpb.DataMessage_Quote_NORMAL.Enum(),
			}
		}
	case MessageEdit:
		_, targetTimestamp := parseMessageID(message.ID)
		content.EditMessage = &signalpb.EditMessage{
			TargetSentTimestamp: &targetTimestamp,
			DataMessage: &signalpb.DataMessage{
				Timestamp: &messageTimestamp,
				Body:      &message.Body,
			},
		}
	case MessageReaction:
		targetAccountID, targetTimestamp := parseMessageID(message.ID)
		content.DataMessage = &signalpb.DataMessage{
			Timestamp: &messageTimestamp,
			Reaction: &signalpb.DataMessage_Reaction{
				Emoji:               &message.Reaction.Emoji,
				Remove:              &message.Reaction.Remove,
				TargetAuthorAci:     ptrTo(targetAccountID.String()),
				TargetSentTimestamp: &targetTimestamp,
			},
		}
	default:
		s.gateway.log.Error().Msgf("Refusing to send unknown message type '%v'", message.Kind)
		return "", nil
	}

	result := s.client.SendMessage(context.Background(), libsignalgo.NewACIServiceID(recipientID), content)
	if !result.WasSuccessful {
		return "", fmt.Errorf("error sending message: %s", result.Error)
	}

	s.gateway.log.Debug().Any("message", content).Stringer("recipient", recipientID).Msgf("Sent message")
	return makeMessageID(s.client.Store.ACI, messageTimestamp), nil
}

// SendTyping sends a typing notification from us to a given contact on Signal.
func (s *Session) SendTyping(typing Typing) error {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return fmt.Errorf("cannot send typing notification for unauthenticated session")
	}

	recipientID, err := uuid.Parse(typing.SenderID)
	if err != nil {
		return fmt.Errorf("failed parsing '%s' as UUID", typing.SenderID)
	}

	var content = &signalpb.Content{
		TypingMessage: &signalpb.TypingMessage{
			Timestamp: ptrTo(makeMessageTimestamp()),
			Action:    ptrTo(typing.State.toSignal()),
		},
	}

	result := s.client.SendMessage(context.Background(), libsignalgo.NewACIServiceID(recipientID), content)
	if !result.WasSuccessful {
		return fmt.Errorf("error sending typing notification: %s", result.Error)
	}

	return nil
}

// SendReceipt sends a read receipt for for a given set of messages to Signal.
func (s *Session) SendReceipt(receipt Receipt) error {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return fmt.Errorf("cannot send receipt for unauthenticated session")
	}

	recipientID, err := uuid.Parse(receipt.SenderID)
	if err != nil {
		return fmt.Errorf("failed parsing '%s' as UUID", receipt.SenderID)
	}

	var timestamps []uint64
	for _, id := range receipt.MessageIDs {
		_, ts := parseMessageID(id)
		timestamps = append(timestamps, ts)
	}

	var content = &signalpb.Content{
		ReceiptMessage: &signalpb.ReceiptMessage{
			Timestamp: timestamps,
			Type:      signalpb.ReceiptMessage_READ.Enum(),
		},
	}

	result := s.client.SendMessage(context.Background(), libsignalgo.NewACIServiceID(recipientID), content)
	if !result.WasSuccessful {
		return fmt.Errorf("error sending receipt: %s", result.Error)
	}

	return nil
}

// SendDelete sends a "Delete for Everyone" message to Signal for a given message ID.
func (s *Session) SendDelete(delete Delete) error {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return fmt.Errorf("cannot send delete for unauthenticated session")
	}

	recipientID, err := uuid.Parse(delete.ChatID)
	if err != nil {
		return fmt.Errorf("failed parsing '%s' as UUID", delete.ChatID)
	}

	_, messageTimestamp := parseMessageID(delete.MessageID)
	var content = &signalpb.Content{
		DataMessage: &signalpb.DataMessage{
			Timestamp: ptrTo(makeMessageTimestamp()),
			Delete: &signalpb.DataMessage_Delete{
				TargetSentTimestamp: &messageTimestamp,
			},
		},
	}

	result := s.client.SendMessage(context.Background(), libsignalgo.NewACIServiceID(recipientID), content)
	if !result.WasSuccessful {
		return fmt.Errorf("error sending delete: %s", result.Error)
	}

	return nil
}

// GetContact returns a concrete [Contact] representation for the account ID given. If no contact
// information could be found, an error will be returned.
func (s *Session) GetContact(id string) (Contact, error) {
	if s.client == nil || s.client.Store.ACI == uuid.Nil {
		return Contact{}, fmt.Errorf("cannot send message for unauthenticated session")
	}

	contactID, err := uuid.Parse(id)
	if err != nil {
		return Contact{}, fmt.Errorf("failed parsing '%s' as UUID", id)
	}

	var contact Contact
	var ctx = context.Background()

	if data, err := s.client.ContactByACI(ctx, contactID); err != nil {
		return Contact{}, fmt.Errorf("failed fetching contact from store: %s", err)
	} else if contact, err = newContact(ctx, s.client, data); err != nil {
		return Contact{}, fmt.Errorf("failed initializing contact: %s", err)
	}

	return contact, nil
}

// HandleClientEvent processes the given incoming Signal client event, checking its concrete type
// and propagating it to the adapter event handler. Unknown or unhandled events are ignored, and any
// errors that occur during processing are logged.
func (s *Session) handleClientEvent(e events.SignalEvent) bool {
	var ctx = context.Background()
	s.gateway.log.Debug().Any("data", e).Msgf("Handling event '%T'", e)

	switch e := e.(type) {
	case *events.ContactList:
		for _, c := range e.Contacts {
			s.propagateEvent(newContactEvent(ctx, s.client, c))
		}
	case *events.ChatEvent:
		s.propagateEvent(newMessageEvent(ctx, s.client, e))
	case *events.Receipt:
		s.propagateEvent(newReceiptEvent(ctx, s.client, e))
	case *events.ReadSelf:
		for _, msg := range e.Messages {
			s.propagateEvent(newSelfReceiptEvent(ctx, msg))
		}
	}

	return true
}

// SetEventHandler assigns the given handler function for propagating internal events into the Python
// gateway. Note that the event handler function is not entirely safe to use directly, and all calls
// should instead be sent to the [Gateway] via its internal call channel.
func (s *Session) SetEventHandler(h HandleEventFunc) {
	s.eventHandler = h
}

// PropagateEvent handles the given event kind and payload with the adapter event handler defined in
// [Session.SetEventHandler].
func (s *Session) propagateEvent(kind EventKind, payload *EventPayload) {
	if s.eventHandler == nil || kind == EventUnknown {
		return
	}

	// Send empty payload instead of a nil pointer, as Python has trouble handling the latter.
	if payload == nil {
		payload = &EventPayload{}
	}

	s.gateway.callChan <- func() { s.eventHandler(kind, payload) }
}

// PtrTo returns a pointer to the given value, and is used for convenience when converting between
// concrete and pointer values without assigning to a variable.
func ptrTo[T any](t T) *T {
	return &t
}
