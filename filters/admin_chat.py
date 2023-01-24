from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from data.config import ADMINS


class IsAdmin(BoundFilter):
    async def check(self, message: Message) -> bool:
        return message.from_user.id in ADMINS
