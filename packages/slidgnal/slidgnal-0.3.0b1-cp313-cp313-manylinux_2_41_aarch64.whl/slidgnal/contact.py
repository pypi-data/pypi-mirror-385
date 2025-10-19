from typing import TYPE_CHECKING

from slidge import LegacyContact, LegacyRoster
from slidge.util.types import Avatar

from .generated import signal

if TYPE_CHECKING:
    from .session import Session


class Contact(LegacyContact[str]):
    session: "Session"

    CORRECTION = True
    REACTIONS_SINGLE_EMOJI = True

    async def update_info(self, data: signal.Contact | None = None) -> None:
        if not data:
            data = self.session.signal.GetContact(self.legacy_id)
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
