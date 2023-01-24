from aiogram import Dispatcher

from .private_chat import IsPrivate
from .admin_chat import IsAdmin


def setup(dp: Dispatcher):
    dp.filters_factory.bind(IsPrivate, IsAdmin)
