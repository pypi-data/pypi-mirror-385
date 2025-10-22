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
	"go.mau.fi/mautrix-signal/pkg/signalmeow/protobuf/backuppb"
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

	// Maximum number of times we'll attempt to retry connecting to Signal on login or startup.
	connectMaxRetries = 6

	// The amount of time we'll wait for before attempting to reconnect to Signal.
	connectRetryWaitDuration = 5 * time.Second

	// The amount of time we'll wait after receiving our first transient disconnection event, and
	// actually propagating that to the adapter (assuming no other non-disconnection events arrive
	// in the meanwhile). The amount of time set here is meant to be slightly above the minimum
	// retry time for WebSocket connections, usually 5 seconds.
	disconnectGraceDuration = 10 * time.Second
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
		return fmt.Errorf("failed to stop connection: %s", err)
	}
	if err := s.client.Unlink(ctx); err != nil {
		return fmt.Errorf("failed to unlink device: %s", err)
	}
	if err := s.gateway.store.DeleteDevice(ctx, &s.client.Store.DeviceData); err != nil {
		return fmt.Errorf("failed to delete device from store: %s", err)
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

// The context key used for tracking login or connection retries.
type retryCountKey struct{}

// Attach retry count to given [context.Context] for use in subsequent calls.
func contextWithRetryCount(ctx context.Context, count int) context.Context {
	return context.WithValue(ctx, retryCountKey{}, count)
}

// Retrieve retry count from given [context.Context], or return 0 if no existing count was found.
func retryCountFromContext(ctx context.Context) int {
	if count, ok := ctx.Value(retryCountKey{}).(int); ok {
		return count
	}
	return 0
}

// Error messages reported during login.
const (
	errLogin                = "Login failed with error"
	errLoginChannel         = "Failed getting response from login channel"
	errLoginMissingSignalID = "No Signal account ID received in login"
	errLoginStoreDevice     = "Failed storing device data"
	errLoginStoreSignalID   = "No Signal account ID found in store"
	errLoginRetrieveDevice  = "Failed fetching device from store"
	errLoginConnect         = "Failed connecting after login"
	errLoginState           = "Unexpected login state transition"
)

// Process login, propagating events to the pre-set [HandleEventFunc] attached to the [Session].
// This function is expected to be run in a Goroutine, as it will otherwise block for an indefinite
// amount of time.
func (s *Session) login(ctx context.Context) {
	provCtx, provCancel := context.WithCancel(s.gateway.log.WithContext(ctx))
	ctx = contextWithRetryCount(ctx, retryCountFromContext(ctx)+1)

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
				s.gateway.log.Err(resp.Err).Msg(errLoginChannel)
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginChannel}})
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
					s.gateway.log.Error().Msg(errLoginMissingSignalID)
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginMissingSignalID}})
					return
				} else if err := s.gateway.store.PutDevice(ctx, resp.ProvisioningData); err != nil {
					provCancel()
					s.gateway.log.Err(err).Msg(errLoginStoreDevice)
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginStoreDevice}})
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
					s.gateway.log.Error().Msg(errLoginStoreSignalID)
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginStoreSignalID}})
					return
				}
				device, err := s.gateway.store.DeviceByACI(ctx, deviceID)
				if err != nil {
					s.gateway.log.Err(err).Msg(errLoginRetrieveDevice)
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginRetrieveDevice}})
				}
				if err := s.connect(ctx, device); err != nil {
					s.gateway.log.Err(err).Msg(errLoginConnect)
					s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginConnect}})
				}
				return
			// Handle any errors encountered during provisioning.
			case resp.State == signalmeow.StateProvisioningError:
				provCancel()
				s.gateway.log.Err(resp.Err).Msg(errLogin)
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: fmt.Sprintf("%s: %s", errLogin, resp.Err)}})
				return
			// Fallback error handling for unhandled state transitions.
			default:
				provCancel()
				s.gateway.log.Error().Str("state", resp.State.String()).Str("prev", prevState.String()).Msg(errLoginState)
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: errLoginState}})
				return
			}
			prevState = resp.State
		// We've been waiting for an event for some time; see if we're stuck at the initial provisioning
		// stage and retry login if so.
		case <-time.After(loginTimeoutDuration):
			if prevState == signalmeow.StateProvisioningURLReceived {
				provCancel()
				if retryCountFromContext(ctx) > loginMaxRetries {
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
				s.propagateEvent(EventLogin, &EventPayload{Login: Login{Error: fmt.Sprintf("%s: %s", errLogin, err)}})
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

	ctx = contextWithRetryCount(ctx, retryCountFromContext(ctx)+1)

	if err := s.client.RegisterCapabilities(ctx); err != nil {
		s.gateway.log.Err(err).Msg("Failed to register client capabilities")
	}

	connChan, err := s.client.StartReceiveLoops(ctx)
	if err != nil {
		count := retryCountFromContext(ctx)
		if count > connectMaxRetries {
			return fmt.Errorf("failed to start connection: %s", err)
		}

		s.gateway.log.Err(err).Msgf("Failed to start connection, retry attempt %d out of %d", count, connectMaxRetries)
		time.Sleep(connectRetryWaitDuration)

		return s.connect(ctx, device)
	}

	// Handle connection state transitions in background.
	go func() {
		var storedStatus signalmeow.SignalConnectionStatus
		for {
			// Read stored connection status if set by a previous iteration, or read fresh status
			// from connection channel if no stored status is found.
			var status signalmeow.SignalConnectionStatus
			if storedStatus.Event != signalmeow.SignalConnectionEventNone {
				status = storedStatus
				storedStatus = signalmeow.SignalConnectionStatus{}
			} else {
				var ok bool
				if status, ok = <-connChan; !ok {
					s.gateway.log.Debug().Msg("Connection channel closed, stopping connection")
					return
				}
			}

			switch status.Event {
			case signalmeow.SignalConnectionEventConnected:
				s.propagateEvent(EventConnect, &EventPayload{Connect: Connect{
					AccountID:   s.client.Store.ACI.String(),
					PhoneNumber: s.client.Store.Number,
				}})
			case signalmeow.SignalConnectionEventDisconnected:
				// Wait for some time before actually sending through disconnection event, as these
				// can be transient in nature; if any non-disconnect events arrive before then, handle
				// that immediately.
				disconnectTimer := time.NewTimer(disconnectGraceDuration)

			EventLoop:
				for {
					// Continue reading connection events from channel, jumping out on the first
					// non-disconnect event or if our graceful disconnect timer expires.
					var ok bool
					select {
					case storedStatus, ok = <-connChan:
						if !ok {
							s.gateway.log.Debug().Msg("Connection channel closed, stopping connection")
							return
						}
						if storedStatus.Event != signalmeow.SignalConnectionEventDisconnected {
							break EventLoop
						}
					case <-disconnectTimer.C:
						break EventLoop
					}
				}

				if storedStatus.Event == signalmeow.SignalConnectionEventDisconnected {
					// Reset stored status for next iteration since there's nothing else to handle.
					storedStatus = signalmeow.SignalConnectionStatus{}

					// Only send disconnect event if timer actually expired before reaching this point.
					if !disconnectTimer.Stop() {
						var reason = "unknown error occured"
						if storedStatus.Err != nil {
							reason = storedStatus.Err.Error()
						}
						s.propagateEvent(EventConnect, &EventPayload{Connect: Connect{Error: fmt.Sprintf("Connection failed: %s", reason)}})
					}
				}
			case signalmeow.SignalConnectionEventLoggedOut:
				if err := s.Disconnect(); err != nil {
					s.gateway.log.Err(err).Msg("Failed to disconnect on logout event")
				}
				var reason string
				if status.Err != nil {
					reason = status.Err.Error()
				}
				s.propagateEvent(EventLogout, &EventPayload{Logout: Logout{Reason: reason}})
				s.client = nil
			case signalmeow.SignalConnectionCleanShutdown:
				// We've been logged out on what appears to be a clean shutdown, send logout event.
				if !s.client.IsLoggedIn() {
					s.propagateEvent(EventLogout, nil)
				}
				s.client = nil
			case signalmeow.SignalConnectionEventError:
				s.propagateEvent(EventConnect, &EventPayload{Connect: Connect{Error: fmt.Sprintf("Connection failed: %s", status.Err)}})
				s.client = nil
			}
		}
	}()

	// Synchronize chats to storage.
	if s.client.Store.EphemeralBackupKey != nil {
		go func() {
			if err := s.syncArchive(ctx); err != nil {
				s.gateway.log.Err(err).Msg("Failed synchronizing chat archive")
				return
			}
			if s.client.Store.MasterKey != nil {
				s.client.SyncStorage(ctx)
			}
		}()
	} else if s.client.Store.MasterKey != nil {
		go s.client.SyncStorage(ctx)
	}

	return nil
}

// SyncArchive fetches and processes the chat archive (potentially) given to us by the main device
// during linking. Transient errors may have the process retried, but refusal of transfer will
// result in no more attempts to sync.
func (s *Session) syncArchive(ctx context.Context) error {
	if s.device.ArchiveSynced {
		return nil
	}

	if s.client.Store.EphemeralBackupKey != nil {
		meta, err := s.client.WaitForTransfer(ctx)
		if err != nil {
			return fmt.Errorf("error waiting for archive transfer: %s", err)
		} else if meta.Error != "" {
			s.device.ArchiveSynced = true
			s.propagateEvent(EventArchiveSync, &EventPayload{ArchiveSync: ArchiveSync{Error: meta.Error}})
			return nil
		}

		if err = s.client.FetchAndProcessTransfer(ctx, meta); err != nil {
			return fmt.Errorf("error fetching and processing archive: %s", err)
		}
	}

	s.device.ArchiveSynced = true
	s.propagateEvent(EventArchiveSync, nil)
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

	var ctx = context.Background()
	var content = &signalpb.Content{}

	// Set default values for internal fields.
	message.Timestamp = makeMessageTimestamp()

	switch message.Kind {
	case MessagePlain:
		content.DataMessage = newSignalDataMessage(message)
	case MessageAttachment:
		if len(message.Attachments) != 1 {
			return "", fmt.Errorf("invalid number of attachments in message, expected 1, got %d", len(message.Attachments))
		}

		attachment := message.Attachments[0]
		ptr, err := s.client.UploadAttachment(ctx, attachment.Data)
		if err != nil {
			return "", fmt.Errorf("failed uploading attachment to Signal: %s", err)
		}

		if attachment.ContentType == "" {
			attachment.ContentType = detectContentType(attachment.Data)
		}

		ptr.ContentType = &attachment.ContentType
		ptr.FileName = &message.Body
		if attachment.Filename != "" {
			ptr.FileName = &attachment.Filename
		}

		// TODO: Set width and height for images.
		// TODO: Convert voice-messages and animaged GIFs as-needed.

		content.DataMessage = newSignalDataMessage(message)
		content.DataMessage.Attachments = []*signalpb.AttachmentPointer{ptr}
	case MessageEdit:
		_, targetTimestamp := parseMessageID(message.ID)
		content.EditMessage = &signalpb.EditMessage{
			TargetSentTimestamp: &targetTimestamp,
			DataMessage: &signalpb.DataMessage{
				Timestamp: &message.Timestamp,
				Body:      &message.Body,
			},
		}
	case MessageReaction:
		targetAccountID, targetTimestamp := parseMessageID(message.ID)
		content.DataMessage = &signalpb.DataMessage{
			Timestamp: &message.Timestamp,
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

	result := s.client.SendMessage(ctx, libsignalgo.NewACIServiceID(recipientID), content)
	if !result.WasSuccessful {
		return "", fmt.Errorf("error sending message: %s", result.Error)
	}

	s.gateway.log.Debug().Any("message", content).Stringer("recipient", recipientID).Msgf("Sent message")
	return makeMessageID(s.client.Store.ACI, message.Timestamp), nil
}

// NewSignalDataMessage returns a valid [signalpb.DataMessage] from the given internal [Message]
// instance, setting values as-needed.
func newSignalDataMessage(message Message) *signalpb.DataMessage {
	var data = &signalpb.DataMessage{
		Timestamp: &message.Timestamp,
		Body:      &message.Body,
	}

	if message.ReplyTo.ID != "" {
		replyAuthor, replyTimestamp := parseMessageID(message.ReplyTo.ID)
		data.Quote = &signalpb.DataMessage_Quote{
			Id:        &replyTimestamp,
			AuthorAci: ptrTo(replyAuthor.String()),
			Text:      &message.ReplyTo.Body,
			Type:      signalpb.DataMessage_Quote_NORMAL.Enum(),
		}
	}

	return data
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

	s.gateway.log.Debug().Any("typing", content).Stringer("recipient", recipientID).Msgf("Sent typing notification")
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

	s.gateway.log.Debug().Any("receipt", content).Stringer("recipient", recipientID).Msgf("Sent receipt")
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

	s.gateway.log.Debug().Any("delete", content).Stringer("recipient", recipientID).Msgf("Sent delete")
	return nil
}

// GetBackupContacts fetches any contacts stored in local backup, which is usually populated by
// archive transfer during initial connection. Contact information returned may be partial.
func (s *Session) GetBackupContacts() ([]Contact, error) {
	ctx := context.Background()
	chats, err := s.client.Store.BackupStore.GetBackupChats(ctx)
	if err != nil {
		return nil, fmt.Errorf("error getting chats from backup store: %s", err)
	}

	var contacts []Contact
	for _, chat := range chats {
		r, err := s.client.Store.BackupStore.GetBackupRecipient(ctx, chat.RecipientId)
		if err != nil {
			s.gateway.log.Err(err).Msg("Failed to get recipient from backup")
			continue
		}

		switch d := r.Destination.(type) {
		case *backuppb.Recipient_Contact:
			// Ignore and remove direct chat with no messages.
			if chat.TotalMessages == 0 {
				_ = s.client.Store.BackupStore.DeleteBackupChat(ctx, chat.Id)
				continue
			}

			aci, pni := castUUID(d.Contact.GetAci()), castUUID(d.Contact.GetPni())
			r, err := s.client.Store.RecipientStore.LoadAndUpdateRecipient(ctx, aci, pni, nil)
			if err != nil {
				s.gateway.log.Err(err).Msg("Failed getting recipient data")
				continue
			}

			c, err := newContact(ctx, s.client, r)
			if err != nil {
				s.gateway.log.Err(err).Msg("Failed initializing contact from backup")
			} else if c.ID != "" {
				contacts = append(contacts, c)
			}

		}
	}

	return contacts, nil
}

// GetContact returns a concrete [Contact] representation for the account ID given. If no contact
// information could be found, an empty contact will be returned with no error.
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
