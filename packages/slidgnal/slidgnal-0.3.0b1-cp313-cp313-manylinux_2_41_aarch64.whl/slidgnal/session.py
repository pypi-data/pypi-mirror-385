import asyncio
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, Union

from slidge import BaseSession, GatewayUser
from slidge.util.types import MessageReference
from slixmpp.exceptions import XMPPError

from .contact import Contact, Roster
from .gateway import Gateway
from .generated import go, signal

MESSAGE_LOGIN_SUCCESS = (
    "Login successful! You might need to repeat this process in the future if the Linked Device "
    "is re-registered from your main device."
)

MESSAGE_LOGGED_OUT = (
    "You have been logged out, please use the re-login adhoc command and re-scan the QR code on "
    "your main device."
)

Recipient = Union["Contact", "MUC"]


class Session(BaseSession[str, Recipient]):
    contacts: "Roster"
    bookmarks: "Bookmarks"
    xmpp: "Gateway"

    def __init__(self, user: GatewayUser):
        super().__init__(user)
        try:
            device = signal.LinkedDevice(ID=self.user.legacy_module_data["device_id"])
        except KeyError:
            device = signal.LinkedDevice()
        self.signal = signal.NewSession(self.xmpp.signal, device)
        self.__handle_event = make_sync(self.handle_event, self.xmpp.loop)
        self.signal.SetEventHandler(self.__handle_event)
        self.__message_reactions: dict[str, str] = {}
        self.__message_ids: dict[str, str] = {}

    async def login(self):
        self.__reset_connected()
        self.signal.Login()
        return await self.__connected

    async def handle_event(self, event, ptr):
        """
        Handle incoming event, as propagated by the Signal adapter. Typically, events carry all
        state required for processing by the Gateway itself, and will do minimal processing
        themselves.
        """
        data = signal.EventPayload(handle=ptr)
        if event == signal.EventLogin:
            await self.handle_login(data.Login)
        if event == signal.EventConnect:
            await self.handle_connect(data.Connect)
        if event == signal.EventContact:
            await self.handle_contact(data.Contact)
        if event == signal.EventMessage:
            await self.handle_message(data.Message)
        elif event == signal.EventTyping:
            await self.handle_typing(data.Typing)
        elif event == signal.EventReceipt:
            await self.handle_receipt(data.Receipt)
        elif event == signal.EventDelete:
            await self.handle_delete(data.Delete)

    async def handle_login(self, data: signal.Login):
        if data.QRCode:
            self.send_gateway_status("QR Scan Needed", show="dnd")
            await self.send_qr(data.QRCode)
        elif data.DeviceID:
            self.send_gateway_message(MESSAGE_LOGIN_SUCCESS)
            self.legacy_module_data_set({"device_id": data.DeviceID})
        elif data.Error:
            self.send_gateway_status("Login error", show="dnd")
            self.send_gateway_message(data.Error)

    async def handle_connect(self, data: signal.Connect):
        if self.__connected.done():
            if data.Error:
                self.send_gateway_status("Connection error", show="dnd")
                self.send_gateway_message(data.Error)
            else:
                self.send_gateway_status(f"Connected as {self.user_phone}", show="chat")
        elif data.Error:
            self.xmpp.loop.call_soon_threadsafe(
                self.__connected.set_exception,
                XMPPError("internal-server-error", data.Error),
            )
        else:
            self.contacts.user_legacy_id = data.AccountID
            self.user_phone = data.PhoneNumber
            self.xmpp.loop.call_soon_threadsafe(
                self.__connected.set_result, f"Connected as {self.user_phone}"
            )

    async def handle_contact(self, data: signal.Contact):
        contact = await self.contacts.by_legacy_id(data.ID)
        await contact.update_info(data)
        await contact.add_to_roster()

    async def handle_message(self, data: signal.Message):
        recipient = await self.__get_recipient(
            data.SenderID, data.ChatID, data.IsCarbon
        )
        message_id = str(
            self.__get_original_message_id(data.TargetID) or data.TargetID or data.ID,
        )
        message_timestamp = (
            datetime.fromtimestamp(data.Timestamp, tz=timezone.utc)
            if data.Timestamp > 0
            else None
        )
        if data.Kind == signal.MessagePlain:
            recipient.send_text(
                body=data.Body,
                legacy_msg_id=message_id,
                when=message_timestamp,
                reply_to=await self.__get_reply_to(data.ReplyTo),
                carbon=data.IsCarbon,
            )
        elif data.Kind == signal.MessageReaction:
            emojis = [] if data.Reaction.Remove else [data.Reaction.Emoji]
            recipient.react(
                legacy_msg_id=message_id,
                emojis=emojis,
                carbon=data.IsCarbon,
            )
        elif data.Kind == signal.MessageEdit:
            recipient.correct(
                legacy_msg_id=message_id,
                new_text=data.Body,
                when=message_timestamp,
                reply_to=await self.__get_reply_to(data.ReplyTo),
                carbon=data.IsCarbon,
            )
            self.__set_original_message_id(data.ID, message_id)

    async def handle_typing(self, data: signal.Typing):
        """
        Handle incoming typing notification, as propagated by the Signal adapter.
        """
        recipient = await self.__get_recipient(data.SenderID)
        if data.State == signal.TypingStateStarted:
            recipient.composing()
        elif data.State == signal.TypingStateStopped:
            recipient.paused()

    async def handle_receipt(self, data: signal.Receipt):
        """
        Handle incoming delivered/read receipt, as propagated by the Signal adapter.
        """
        recipient = await self.__get_recipient(data.SenderID)
        for message_id in data.MessageIDs:
            if data.Kind == signal.ReceiptDelivered:
                recipient.received(message_id)
            elif data.Kind == signal.ReceiptRead:
                recipient.displayed(legacy_msg_id=message_id, carbon=data.IsCarbon)

    async def handle_delete(self, data: signal.Delete):
        """
        Handle incoming message deletion, as propagated by the Signal adapter.
        """
        recipient = await self.__get_recipient(
            data.AuthorID, data.ChatID, data.IsCarbon
        )
        recipient.retract(legacy_msg_id=data.MessageID, carbon=data.IsCarbon)

    async def on_text(
        self,
        chat: Recipient,
        text: str,
        *,
        reply_to_msg_id: str | None = None,
        reply_to_fallback_text: str | None = None,
        reply_to=None,
        **_,
    ):
        """
        Send outgoing plain-text message to given Signal contact.
        """
        message = signal.Message(
            Kind=signal.MessagePlain,
            ChatID=chat.legacy_id,
            Body=text,
        )
        message = self.__set_reply_to(
            chat, message, reply_to_msg_id, reply_to_fallback_text, reply_to
        )
        return self.signal.SendMessage(message)

    async def on_react(
        self, chat: Recipient, legacy_msg_id: str, emojis: list[str], thread=None
    ):
        """
        Send or remove emoji reaction to existing Signal message. Slidge core makes sure that the
        emojis parameter is always empty or a *single* emoji.
        """
        message = signal.Message(
            Kind=signal.MessageReaction,
            ID=legacy_msg_id,
            ChatID=chat.legacy_id,
        )
        if emojis:
            message.Reaction = signal.Reaction(Emoji=emojis[0], Remove=False)
        else:
            previous_reaction = self.__get_message_reaction(legacy_msg_id)
            if not previous_reaction:
                raise XMPPError(
                    "not-acceptable", "Existing reaction not found, cannot remove"
                )
            message.Reaction = signal.Reaction(Emoji=previous_reaction, Remove=True)
        self.signal.SendMessage(message)
        if emojis:
            self.__set_message_reaction(legacy_msg_id, emojis[0])

    async def on_correct(
        self,
        chat: Recipient,
        text: str,
        legacy_msg_id: str,
        thread=None,
        link_previews=(),
        mentions=None,
    ):
        """
        Request correction (aka editing) for a given Signal message.
        """
        message = signal.Message(
            Kind=signal.MessageEdit,
            ID=legacy_msg_id,
            ChatID=chat.legacy_id,
            Body=text,
        )
        self.signal.SendMessage(message)

    async def on_presence(self, *args, **kwargs):
        """
        Signal doesn't support contact presence, so calls to this function are no-ops.
        """
        pass

    async def on_active(self, *args, **kwargs):
        """
        Signal has no equivalent to the "active" chat state, so calls to this function are no-ops.
        """
        pass

    async def on_inactive(self, *args, **kwargs):
        """
        Signal has no equivalent to the "inactive" chat state, so calls to this function are no-ops.
        """
        pass

    async def on_composing(self, chat: Recipient, thread=None):
        """
        Send "started" typing state to given Signal contact, signifying that a message is currently
        being composed.
        """
        typing = signal.Typing(
            SenderID=chat.legacy_id,
            Typing=signal.Typing(State=signal.TypingStateStarted),
        )
        self.signal.SendTyping(typing)

    async def on_paused(self, chat: Recipient, thread=None):
        """
        Send "stopped" typing state to given Signal contact, signifying that an (unsent) message is
        no longer being composed.
        """
        typing = signal.Typing(
            SenderID=chat.legacy_id,
            Typing=signal.Typing(State=signal.TypingStateStopped),
        )
        self.signal.SendTyping(typing)

    async def on_displayed(self, c: Recipient, legacy_msg_id: str, thread=None):
        """
        Send "read" receipt, signifying that the Signal message sent has been displayed on the XMPP
        client.
        """
        receipt = signal.Receipt(
            SenderID=c.legacy_id,
            MessageIDs=go.Slice_string([legacy_msg_id]),
        )
        self.signal.SendReceipt(receipt)

    async def on_retract(self, c: Recipient, legacy_msg_id: str, thread=None):
        """
        Request deletion (aka retraction) for a given Signal message.
        """
        delete = signal.Delete(
            ChatID=c.legacy_id,
            MessageID=legacy_msg_id,
        )
        self.signal.SendDelete(delete)

    async def __get_recipient(
        self,
        legacy_sender_id: str,
        legacy_chat_id: str | None = None,
        is_carbon: bool = False,
    ) -> Recipient:
        """
        Return correct recipient for given references to sender and chat IDs, the latter of which
        can either represent another contact, or a group-chat.
        """
        if legacy_chat_id is not None:
            if is_carbon:
                return await self.contacts.by_legacy_id(legacy_chat_id)
            elif legacy_sender_id != legacy_chat_id:
                raise XMPPError(
                    "bad-request", "Group-chat support is not implemented yet"
                )
        return await self.contacts.by_legacy_id(legacy_sender_id)

    async def __get_reply_to(self, data: signal.Reply) -> Optional[MessageReference]:
        """
        Get message reference for reply data, or return None.
        """
        if not data.ID:
            return None
        reply_to = MessageReference(
            legacy_id=data.ID,
            body=data.Body,
        )
        if data.AuthorID == self.contacts.user_legacy_id:
            reply_to.author = "user"
        else:
            reply_to.author = await self.contacts.by_legacy_id(data.AuthorID)
        return reply_to

    def __set_reply_to(
        self,
        chat: Recipient,
        message: signal.Message,
        reply_to_msg_id: Optional[str] = None,
        reply_to_fallback_text: Optional[str] = None,
        reply_to=None,
    ):
        """
        Sets ReplyTo fields for given Message, returning the Message.
        """
        if reply_to_msg_id:
            message.ReplyTo.ID = reply_to_msg_id
        if reply_to:
            message.ReplyTo.AuthorID = (
                reply_to.contact.legacy_id if chat.is_group else chat.legacy_id
            )
        if reply_to_fallback_text:
            message.ReplyTo.Body = strip_quote_prefix(reply_to_fallback_text)
            message.Body = message.Body.lstrip()
        return message

    def __set_original_message_id(
        self,
        new_legacy_message_id: str,
        original_legacy_msg_id: str,
    ) -> None:
        """
        Set new message ID to original message ID mapping.
        """
        self.__message_ids[new_legacy_message_id] = original_legacy_msg_id

    def __get_original_message_id(
        self,
        new_legacy_message_id: str,
    ) -> str | None:
        """
        Get original message ID for given new message ID.
        """
        return self.__message_ids.get(new_legacy_message_id, None)

    def __set_message_reaction(
        self,
        legacy_msg_id: str,
        emoji: str,
    ) -> None:
        """
        Set message reaction reference for a legacy message ID.
        """
        self.__message_reactions[legacy_msg_id] = emoji

    def __get_message_reaction(
        self,
        legacy_msg_id: str,
    ) -> str | None:
        """
        Get message reaction reference for a legacy message ID.
        """
        return self.__message_reactions.pop(legacy_msg_id, None)

    def __reset_connected(self):
        if hasattr(self, "_connected") and not self.__connected.done():
            self.xmpp.loop.call_soon_threadsafe(self.__connected.cancel)
        self.__connected: asyncio.Future[str] = self.xmpp.loop.create_future()


def strip_quote_prefix(text: str):
    """
    Return multi-line text without leading quote marks (i.e. the ">" character).
    """
    return "\n".join(x.lstrip(">").strip() for x in text.split("\n")).strip()


def make_sync(func, loop):
    """
    Wrap async function in synchronous operation, running against the given loop in thread-safe mode.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            future = asyncio.run_coroutine_threadsafe(result, loop)
            return future.result()
        return result

    return wrapper
