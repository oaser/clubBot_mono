from datetime import datetime
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery
from aiogram.utils.json import json
from aiohttp import ClientSession

from data.config import BIG_TEXT, PERIOD, PROVIDER_TOKEN, DOMAIN, MONO_WEBHOOK_PATH, PRICE, ADMINS
from filters import IsPrivate
from keyboard.inline.choice_buttons import start_keyboard, menu_keyboard_halfreg, approval_keyboard, menu_exit_keyboard, \
    menu_keyboard_fullreg, quantity_keyboard, menu_keyboard_subsonly, menu_keyboard_regonly, invoice_keyboard, \
    menu_keyboard_admin
from loader import dp
from utils import database, states
from utils.database import Customer

db = database.DBCommands()

WEBHOOK_HOST = DOMAIN
WEBHOOK_URL = f'{WEBHOOK_HOST}/{MONO_WEBHOOK_PATH}'


@dp.message_handler(IsPrivate(), Command('start', prefixes='/'))
@dp.message_handler(IsPrivate(), Command('start', prefixes='/'), state='*')
async def start_phone_request(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    user_id = message.from_user.id
    customer = await db.get_customer(user_id)
    if customer:
        if customer.subs_check:
            await states.MainMenu.full_reg.set()
            return await main_menu(call=message, state=state)
        else:
            await states.MainMenu.half_reg.set()
            return await main_menu(call=message, state=state)
    else:
        markup = await start_keyboard()
        current_message = await message.answer(text='Підтвердьте номер телефону', reply_markup=markup)
        current_data.update({'message': current_message})
        await state.set_data(current_data)


@dp.message_handler(IsPrivate(), content_types=types.ContentType.CONTACT)
@dp.message_handler(IsPrivate(), content_types=types.ContentType.CONTACT, state='*')
async def registration_phone(message: Message, state: FSMContext):
    date = datetime.now().timestamp()

    if message.from_user.id == message.contact.user_id:
        new_customer = await db.add_new_customer(message=message, date=date)
    else:
        return 

    if new_customer:
        await states.MainMenu.half_reg.set()
        return await main_menu(call=message, state=state)
    else:
        old_customer: Customer = await db.get_customer(message.from_user.id)

        if old_customer.subs_check:
            await states.MainMenu.full_reg.set()
            await main_menu(call=message, state=state)
        else:
            await states.MainMenu.half_reg.set()
            return await main_menu(call=message, state=state)


@dp.message_handler(IsPrivate(), text='Вступити до клубу', state='*')
async def registration_start(call: Union[CallbackQuery, Message], state: FSMContext):
    current_data: dict = await state.get_data()

    text = 'Як тебе звати? (Приклад: Володимир Зеленський)'
    if isinstance(call, CallbackQuery):
        await dp.bot.answer_callback_query(call.id)
        current_message = await call.message.edit_text(text=text)
    else:
        current_message = await call.answer(text=text, reply_markup=ReplyKeyboardRemove())

    current_data.update({'message': current_message})
    await state.set_data(current_data)
    await states.RegMenu.reg_name.set()


@dp.message_handler(IsPrivate(), regexp=r"^([А-Я,а-я-ЁёІіЇї]+ [А-Я,а-я-ЁёІіЇї]+)$", state=[states.RegMenu.reg_name])
async def registration_name(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await corrector(message=message, state=state)
        return
    current_data: dict = await state.get_data()
    name = message.text.lower()
    current_data.update({'name': name})
    text = 'Скільки років? (Приклад: 47)'

    current_message = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    current_data.update({'message': current_message})
    await state.set_data(current_data)
    await states.RegMenu.reg_age.set()


@dp.message_handler(IsPrivate(), regexp=r"^([1-9]|[1-9]\d|[1][0-5]\d)$", state=[states.RegMenu.reg_age])
async def registration_age(message: Message, state: FSMContext):
    # if len(message.text) > 3:
    #     await corrector(message=message, state=state)
    #     return
    current_data: dict = await state.get_data()
    age = int(message.text)
    current_data.update({'age': age})
    text = 'З якого ви міста? (Приклад: Київ)'

    current_message = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    current_data.update({'message': current_message})
    await state.set_data(current_data)
    await states.RegMenu.reg_location.set()


@dp.message_handler(IsPrivate(), regexp=r"^([А-Я,а-я-ЁёІіЇї ]+)$", state=[states.RegMenu.reg_location])
async def registration_location(message: Message, state: FSMContext):
    if len(message.text) > 100:
        await corrector(message=message, state=state)
        return
    current_data: dict = await state.get_data()
    location = message.text.lower()
    current_data.update({'location': location})
    text = f'Все вірно?\n\n' \
           f'Ім\'я: {current_data["name"].title()}\n\n' \
           f'Вік: {current_data["age"]}\n\n' \
           f'Місто: {current_data["location"].capitalize()}'
    markup = await approval_keyboard()

    current_message = await message.answer(text=text, reply_markup=markup)

    current_data.update({'message': current_message})
    await state.set_data(current_data)

    await states.RegMenu.reg_approve.set()


@dp.message_handler(IsPrivate(), text='✅Підтвердити', state=[states.RegMenu.reg_approve])
async def registration_fin(call: Message, state: FSMContext):

    current_data: dict = await state.get_data()
    name = current_data['name']
    age = current_data['age']
    location = current_data['location']
    customer_id = call.from_user.id

    try:
        await db.update_fin_registration(customer_id=customer_id,
                                         pseudonym=name,
                                         age=age,
                                         location=location)
    except Exception as ex:
        print(f'{ex}\n{customer_id} не внесен в базу')
        return

    await states.MainMenu.full_reg.set()

    await invoice_form(message=call, state=state)


@dp.message_handler(IsPrivate(), text='Подовжити підписку клубу', state='*')
async def invoice_form(message: Message, state: FSMContext):
    # current_data: dict = await state.get_data()
    current_state = await state.get_state()
    if current_state == 'Payment:info':
        text = 'На жаль, не вдалося підтвердити вашу участь у клубі.\nВнесіть членський внесок 🧑🏻‍💻\n\n' \
               'Надішліть мені повідомлення з числом <b>місяців</b> на який бажаєте оформити підписку ' \
               'від <b>1</b> до <b>99</b>'
    else:
        text = 'Надішліть мені повідомлення з числом <b>місяців</b> на який бажаєте оформити підписку ' \
               'від <b>1</b> до <b>99</b>'
    await states.Payment.periods.set()

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')


@dp.message_handler(IsPrivate(), regexp=r"^([1-9]|[1-9]\d)$", state=[states.Payment.periods])
async def invoice_set_data(message: Message, state: FSMContext):
    current_data: dict = await state.get_data()
    periods = int(message.text)
    current_data.update({'periods': periods})
    await state.set_data(current_data)
    await states.Payment.checkout.set()
    await get_invoice(call=message, state=state)


# @dp.message_handler(IsPrivate(), text='Продлить подписку клуба', state='*')
# async def invoice_form(call: Message, state: FSMContext):
#     current_data: dict = await state.get_data()
#     periods = 1
#     current_data.update({'periods': periods})
#     markup = await quantity_keyboard()
#     text = 'Какой период подписки желаете оплатить:' \
#            f'<b>{periods*30} дней</b>'
#
#     current_message = await call.answer(text=text, reply_markup=markup)
#     current_data.update({'message': current_message})
#
#     await state.set_data(current_data)
#
#
# @dp.message_handler(IsPrivate(), text='+ 30 дней', state='*')
# async def period_plus(call: Message, state: FSMContext):
#     current_data: dict = await state.get_data()
#     periods = current_data.get('periods')
#     max_periods = 3
#
#     if periods == max_periods or periods is None:
#         return
#     else:
#         periods += 1
#
#     current_data.update({'periods': periods})
#     text = 'Какой период подписки желаете оплатить:' \
#            f'<b>{periods*30} дней</b>'
#
#     markup = await quantity_keyboard()
#
#     await call.answer(text=text, reply_markup=markup)
#
#     await state.set_data(current_data)
#
#
# @dp.message_handler(IsPrivate(), text='- 30 дней', state='*')
# async def period_minus(call: Message, state: FSMContext):
#     current_data: dict = await state.get_data()
#     periods = current_data.get('periods')
#
#     if periods == 1 or periods is None:
#         return
#     else:
#         periods -= 1
#
#     current_data.update({'periods': periods})
#     text = 'Какой период подписки желаете оплатить:' \
#            f'<b>{periods*30} дней</b>'
#
#     markup = await quantity_keyboard()
#
#     await call.answer(text=text, reply_markup=markup)
#
#     await state.set_data(current_data)
#
#
# @dp.message_handler(IsPrivate(), text='✅Подтвердить', state='*')
# async def periods_approve(call: Message, state: FSMContext):
#     await get_invoice(call=call, state=state)


async def get_invoice(call: Message, state: FSMContext):
    current_data: dict = await state.get_data()

    user_id = call.from_user.id
    periods = current_data.get('periods')
    if periods is None:
        periods = 1
    price = PRICE
    amount = price * periods
    if periods == 1:
        months = 'місяць'
    elif periods in [2, 3, 4]:
        months = 'місяці'
    else:
        months = 'місяців'

    # prices = [LabeledPrice(label=f'Підписка на {periods*30} днів', amount=amount*periods)]
    provider_token = PROVIDER_TOKEN

    url = 'https://api.monobank.ua/api/merchant/invoice/create'

    invoice_data_dict = dict(amount=amount,
                             webHookUrl=f"{WEBHOOK_URL}",
                             merchantPaymInfo=dict(reference=f'{user_id},{periods}',
                                                   destination=f'Послуги на {periods} {months}',
                                                   basketOrder=[dict(name='Послуги',
                                                                     qty=periods,
                                                                     sum=price)]))
    invoice_data = json.dumps(invoice_data_dict)

    async with ClientSession() as session:
        res = await session.post(
            url=url,
            data=invoice_data,
            headers={'X-Token': f'{provider_token}'}
        )

    response_data: dict = await res.json()
    invoice_url = response_data.get('pageUrl')
    markup = await invoice_keyboard(url=invoice_url, text=f'Сплатити {amount/100} грн.')
    text = f'Внести членський внесок за {periods} {months} {amount/100} грн.'

    await dp.bot.send_message(chat_id=call.chat.id, text=text, reply_markup=markup)

    # invoice = await dp.bot.send_invoice(chat_id=call.chat.id,
    #                                     title='Підписка',
    #                                     description='Оплата членства у клубі',
    #                                     payload=str(periods),
    #                                     provider_token=provider_token,
    #                                     currency='uah',
    #                                     prices=prices,
    #                                     start_parameter='subs-example')

    # current_data.update({'invoice': invoice})
    # await state.set_data(current_data)


# @dp.pre_checkout_query_handler(lambda query: True, state='*')
# async def checkout(pre_checkout_query: PreCheckoutQuery):
#     await dp.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
#                                            error_message="Щось пішло не так")
#

# @dp.message_handler(content_types=['successful_payment'], state='*')  # aiogram.utils.exceptions.InvalidQueryID: Query is too old and response timeout expired or query id is invalid
# async def got_payment(message: Message, state: FSMContext):
#     current_data: dict = await state.get_data()
#     customer_id = message.from_user.id
#     timestamp_now = int(datetime.now().timestamp())
#     payload = message.successful_payment.invoice_payload
#     period = PERIOD
#     periods = int(payload)
#     customer = await db.get_customer(customer_id=customer_id)
#     markup = await menu_exit_keyboard()
#
#     if timestamp_now > customer.subs_before:
#         subs_before = timestamp_now + period * periods  # ?periods
#
#         await db.update_subs_before(customer_id=customer_id, subs_before=subs_before)
#         current_message = await dp.bot.send_message(chat_id=message.chat.id,
#                                                     text='Вітаю, ти у клубі 🧑🏻‍💻',
#                                                     parse_mode='Markdown',
#                                                     reply_markup=markup)
#     else:
#         subs_before = customer.subs_before + period * periods
#         print_date = datetime.fromtimestamp(subs_before).strftime("%d-%m-%Y")
#
#         await db.update_subs_before(customer_id=customer_id, subs_before=subs_before)
#         current_message = await dp.bot.send_message(chat_id=message.chat.id,
#                                                     text=f'Підписка подовжена до <b>{print_date}</b> 🧑🏻‍💻',
#                                                     parse_mode='HTML',
#                                                     reply_markup=markup)
#
#     current_data.update({'message': current_message})
#     await state.set_data(current_data)


@dp.message_handler(IsPrivate(), text='☰Меню', state='*')
@dp.message_handler(IsPrivate(), Command(['menu'], prefixes='/'), state='*')
async def main_menu(call: Union[CallbackQuery, Message], state: FSMContext):
    current_data: dict = await state.get_data()
    current_state = await state.get_state()
    text = BIG_TEXT
    if isinstance(call, CallbackQuery):
        is_admin = call.message.from_user.id in ADMINS
    else:
        is_admin = call.from_user.id in ADMINS

    if is_admin:
        markup = await menu_keyboard_admin()
    else:
        if current_state == 'MainMenu:full_reg':
            markup = await menu_keyboard_fullreg()
        elif current_state == 'MainMenu:half_reg':
            markup = await menu_keyboard_halfreg()
        else:
            return await start_phone_request(message=call, state=state)

    current_message = await call.answer(text=text, reply_markup=markup, parse_mode='HTML')  # if subs_check

    current_data.update({'message': current_message})
    await state.set_data(current_data)


@dp.message_handler(IsPrivate(), Command('info', prefixes='/'), state='*')
@dp.message_handler(IsPrivate(), text='Перевірити підписку клубу', state='*')
async def info(call: Message, state: FSMContext):
    current_data: dict = await state.get_data()

    customer = await db.get_customer(call.from_user.id)

    if customer:
        if customer.subs_check:
            await states.MainMenu.full_reg.set()
            datetime_db = datetime.fromtimestamp(customer.subs_before)
            if datetime_db > datetime.now():
                customer_subs_date = datetime_db.strftime('%d-%m-%Y')
                text = f'Поточна підписка до <b>{customer_subs_date}</b>'
                markup = await menu_exit_keyboard()
            else:
                # text = f'К сожалению не удалось подтвердить ваше участие в клубе.\nВнесите членский взнос 🧑🏻‍💻'
                # markup = await menu_keyboard_subsonly()
                await states.Payment.info.set()
                return await invoice_form(message=call, state=state)
        else:
            await states.MainMenu.half_reg.set()
            text = f'На жаль, не вдалося підтвердити вашу участь у клубі.\n\n' \
                   f'Завершіть реєстрацію та\nВнесіть членський внесок 🧑🏻‍💻'
            markup = await menu_keyboard_regonly()
    else:
        await states.MainMenu.no_reg.set()
        text = f'Зареєструйся'
        markup = await menu_exit_keyboard()

    current_message = await call.answer(text=text, reply_markup=markup, parse_mode='HTML')

    current_data.update({'message': current_message})
    await state.set_data(current_data)


@dp.message_handler(text='⬅Назад', state='*')
@dp.message_handler(text='⬅Назад')
@dp.throttled(rate=0.5)
async def cancel(call: Union[CallbackQuery, Message], state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'RegMenu:reg_approve':
        await state.reset_state()
        return await registration_start(call=call, state=state)
    if current_state == 'MainMenu:full_reg':
        return await main_menu(call=call, state=state)
    if current_state == 'MainMenu:half_reg':
        return await main_menu(call=call, state=state)
    if current_state == 'MainMenu:no_reg':
        return await main_menu(call=call, state=state)
    if not current_state:
        return await main_menu(call=call, state=state)
#     if current_state == 'AdminMenu:change' or current_state == 'AdminMenu:rollback':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'AdminMenu:panel' or current_state == 'Order:info':
#         await state.reset_state()
#         return await start_choice(message=call, state=state)
#     if current_state == 'AdminMenu:credit':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'AdminMenu:credit_push':
#         await state.reset_state()
#         return await credit_mutation_abc(call=call, state=state)
#     if current_state == 'AdminMenu:credit_upd':
#         await state.reset_state()
#         return await credit_mutation_abc(call=call, state=state)
#     if current_state == 'AdminMenu:instance_menu':
#         await state.reset_state()
#         return await admin_panel(call=call, state=state)
#     if current_state == 'ChangePseudonym:initial':
#         await state.reset_state()
#         await call.message.delete()
#         return
#     if not current_state:
#         return await start_choice(message=call, state=state)


async def delete_messages(state):
    current_data: dict = await state.get_data()
    message = current_data.get('message')

    try:
        await message.delete()
    except Exception as ex:
        print(ex)

    invoice = current_data.pop('invoice', None)
    if invoice:
        try:
            await invoice.delete()
        except Exception as ex:
            print(ex)


@dp.message_handler(IsPrivate(), state=[states.RegMenu.reg_name, states.RegMenu.reg_age, states.RegMenu.reg_location,
                                        states.Payment.periods])
async def corrector(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'RegMenu:reg_name':
        text = 'Невірни формат введення. Спробуйте ім\'я прізвище ' \
               'через пробіл кирилицею, наприклад: Володимир Зеленський'
        await message.answer(text=text)
    if current_state == 'RegMenu:reg_age':
        text = 'Невірни формат введення. Спробуйте ввести число цифрами, наприклад: 47'
        await message.answer(text=text)
    if current_state == 'RegMenu:reg_location':
        text = 'Невірни формат введення. Спробуйте ввести назву міста кирилицею, наприклад: Київ'
        await message.answer(text=text)
    if current_state == 'Payment:periods':
        text = 'Невірни формат введення. Спробуй ввести чило міяців від 1 до 99, цифрами, наприклад: 10'
        await message.answer(text=text)


@dp.message_handler(IsPrivate())
@dp.message_handler(IsPrivate(), state='*')
async def terminator(message):
    try:
        await message.delete()
    except Exception as ex:
        print(ex)
