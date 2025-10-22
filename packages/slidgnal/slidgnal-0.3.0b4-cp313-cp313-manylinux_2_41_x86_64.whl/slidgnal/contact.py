from typing import TYPE_CHECKING

from slidge import LegacyContact, LegacyRoster
from slidge.util.types import Avatar
from slixmpp.exceptions import XMPPError

from .generated import signal

if TYPE_CHECKING:
    from .session import Session


class Contact(LegacyContact[str]):
    session: "Session"

    CORRECTION = True
    REACTIONS_SINGLE_EMOJI = True

    async def update_info(self, data: signal.Contact | None = None) -> None:
        """
        Set fields for contact based on data given, or if none was, as retrieved from Signal.
        """
        if not data:
            data = self.session.signal.GetContact(self.legacy_id)
            if not data:
                raise XMPPError("item-not-found", "Contact not found")
        self.name = data.Name
        self.is_friend = True
        self.set_vcard(full_name=data.Name, phone=str(data.PhoneNumber))
        if data.Avatar.Image:
            await self.set_avatar(Avatar(data=data.Avatar.Image))
        elif data.Avatar.Delete:
            await self.set_avatar(None)
        self.online()


class Roster(LegacyRoster[str, Contact]):
    session: "Session"

    async def fill(self):
        """
        Retrieve contacts from Signal backup, subscribing to their presence and adding to local
        roster.
        """
        for data in self.session.signal.GetBackupContacts():
            contact = await self.by_legacy_id(data.ID)
            contact.update_info(data)
            yield contact
