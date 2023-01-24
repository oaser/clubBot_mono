from aiogram import executor

from data.config import BOT_TOKEN, DOMAIN
from utils.database import create_db
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChatMember

from utils.mono import mono_start
from utils.scheduler import sched
import filters

WEBHOOK_HOST = DOMAIN
WEBHOOK_URL = f'{WEBHOOK_HOST}'

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8000


async def set_default_commands(dp):
    return await dp.bot.set_my_commands(
        commands=[
            BotCommand('info', 'посмотреть баланс'),
            BotCommand('menu', 'Меню')
        ],
        scope=BotCommandScopeDefault()
    )


async def on_startup(dp):
    filters.setup(dp)
    await dp.bot.set_webhook(WEBHOOK_URL)
    await create_db()
    await set_default_commands(dp)
    sched.start()
    await mono_start()


async def shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.delete_webhook()


if __name__ == '__main__':
    from handlers import dp

    executor.start_webhook(
        dispatcher=dp,
        webhook_path=f'/',
        on_startup=on_startup,
        on_shutdown=shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )

