from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loader import dp
from utils.database import DBCommands, Customer

sched = AsyncIOScheduler()
dbc = DBCommands()


async def send_my_message():
    now = int(datetime.now().timestamp())
    customers: list[Customer] = await dbc.get_customers_for_mailing(now=now)
    for custr in customers:
        print_date = datetime.fromtimestamp(custr.subs_before).strftime("%d-%m-%Y")
        text = f'Твоя подписка действительна до {print_date}. \n<b>Не забудь продлить подписку</b>'
        try:
            await dp.bot.send_message(chat_id=custr.customer_id, text=text, parse_mode='HTML')
        except:
            pass
    try:
        await dp.bot.send_message(chat_id='421380320', text='mailing done')
    except:
        pass

sched.add_job(func=send_my_message, trigger='interval', days=1)
