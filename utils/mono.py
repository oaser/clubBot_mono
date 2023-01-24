import base64
import hashlib

import ecdsa

from datetime import datetime

from aiohttp import web

from aiohttp.web_request import Request
from aiohttp.web_response import Response

from data.config import PERIOD, PUB_KEY_BASE64
from keyboard.inline.choice_buttons import menu_exit_keyboard
from loader import dp
from utils import database
from utils.database import Invoice

routes = web.RouteTableDef()
db = database.DBCommands()


async def verification(request: Request):
    pub_key_base64 = PUB_KEY_BASE64
    x_sign_base64 = request.headers.get('X-Sign')
    body_bytes = await request.read()

    pub_key_bytes = base64.b64decode(pub_key_base64)
    signature_bytes = base64.b64decode(x_sign_base64)
    pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())

    ok = pub_key.verify(signature_bytes, body_bytes, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
    return ok


async def get_reference_data(request_body):
    reference_list: list = request_body.get('reference').split(',')
    customer_id = int(reference_list[0])
    periods = int(reference_list[1])
    return customer_id, periods


async def got_payment_mono(request: Request):
    request_body: dict = await request.json()
    customer_id, periods = await get_reference_data(request_body=request_body)
    invoice_id = request_body.get('invoiceId')
    amount = request_body.get('amount')
    status = request_body.get('status')
    period = PERIOD
    timestamp_now = int(datetime.now().timestamp())
    customer = await db.get_customer(customer_id=customer_id)
    markup = await menu_exit_keyboard()

    if timestamp_now > customer.subs_before:
        subs_before = timestamp_now + period * periods  # ?periods
        # print_date = datetime.fromtimestamp(subs_before).strftime("%d-%m-%Y")
        text = 'Вітаю, ти у клубі 🧑🏻‍💻'
    else:
        subs_before = customer.subs_before + period * periods
        print_date = datetime.fromtimestamp(subs_before).strftime("%d-%m-%Y")
        text = f'Підписка подовжена до <b>{print_date}</b> 🧑🏻‍💻'

    find_invoice: Invoice = await db.get_invoice(invoice_id=invoice_id)

    if find_invoice:
        current_status = find_invoice.status

        if current_status == 'created':
            await db.update_invoice_status(invoice_id=invoice_id,
                                           status=status,
                                           date_timestamp=timestamp_now)
            await db.update_subs_before(customer_id=customer_id,
                                        subs_before=subs_before)
            await dp.bot.send_message(chat_id=customer_id,
                                      text=text,
                                      parse_mode='HTML',
                                      reply_markup=markup)
        else:
            print(f'invoice_id: {invoice_id} status success already')
            return
    else:
        print(f'invoice_id: {invoice_id} status success without created')
        return


async def failure_payment_mono(request: Request):
    request_body: dict = await request.json()
    customer_id, _ = await get_reference_data(request_body=request_body)
    text = 'Неуспішна оплата'
    await dp.bot.send_message(chat_id=customer_id, text=text)


async def expired_payment_mono(request: Request):
    request_body: dict = await request.json()
    customer_id, periods = await get_reference_data(request_body=request_body)
    invoice_id = request_body.get('invoiceId')
    amount = request_body.get('amount')
    await dp.bot.send_message(chat_id=421380320, text=f'{invoice_id} sum {amount} is expired')


async def create_payment_status_mono(request: Request):
    request_body: dict = await request.json()
    customer_id, periods = await get_reference_data(request_body=request_body)
    invoice_id = request_body.get('invoiceId')
    amount = request_body.get('amount')
    status = request_body.get('status')
    timestamp_now = int(datetime.now().timestamp())
    await db.add_new_invoice(invoice_id=invoice_id,
                             customer_id=customer_id,
                             amount=amount,
                             periods=periods,
                             date_timestamp=timestamp_now,
                             status=status)


@routes.post('/ggg')
async def handle(request: Request):
    if request.headers.get('content-type') == 'application/json':
        functions_dict = dict(created=create_payment_status_mono,
                              success=got_payment_mono,
                              failure=failure_payment_mono,
                              expired=expired_payment_mono)
        request_body: dict = await request.json()
        request_status = request_body.get('status')
        status_function = functions_dict.get(request_status)

        if status_function:
            if await verification(request=request):
                await status_function(request=request)

        return Response(status=200)
    else:
        return Response(status=403)


mono_app = web.Application()
mono_app.add_routes(routes)


async def mono_start():
    runner = web.AppRunner(mono_app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 5000)
    await site.start()
# web.run_app(app=mono_app, host='127.0.0.1', port=5000)
