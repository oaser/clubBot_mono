from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


async def start_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='Підтвердьте телефон', request_contact=True))
    return markup


async def quantity_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton(text='+ 30 днів'),
               KeyboardButton(text='- 30 днів'))
    markup.row(KeyboardButton(text='✅Підтвердити'))
    markup.row(KeyboardButton(text='⬅Назад'))
    return markup


async def menu_keyboard_halfreg():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton(text='Вступити до клубу'))
    markup.row(KeyboardButton(text='Перевірити підписку клубу'))
    return markup


async def menu_keyboard_regonly():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(KeyboardButton(text='Вступити до клубу'))
    return markup


async def menu_keyboard_fullreg():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='Перевірити підписку клубу'))
    markup.row(KeyboardButton(text='Подовжити підписку клубу'))
    return markup


async def menu_keyboard_admin():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='Перевірити підписку клубу'))
    markup.row(KeyboardButton(text='Подовжити підписку клубу'))
    markup.row(KeyboardButton(text='Адміністративне меню'))
    return markup


async def admin_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='∑ Витяг з бази рахунків'))
    markup.row(KeyboardButton(text='🧑🏻 Активні користувачі'))
    markup.row(KeyboardButton(text='☰Меню'))
    return markup


async def menu_keyboard_subsonly():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='Подовжити підписку клубу'))
    return markup


async def menu_exit_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='☰Меню'))
    return markup


async def approval_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='✅Підтвердити'))
    markup.row(KeyboardButton(text='⬅Назад'))
    return markup


async def back_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='⬅Назад'))
    return markup


# async def admin_start_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Панель администратора',
#                                     callback_data='admin_panel'))
#     markup.row(InlineKeyboardButton(text='Меню блюд',
#                                     callback_data='dish_menu'))
#     markup.row(InlineKeyboardButton(text='Инфо',
#                                     callback_data='info'))
#     return markup
#
#
# async def admin_panel_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Внести изменения в меню',
#                                     callback_data='db_mutation'))
#     markup.row(InlineKeyboardButton(text='Зачислить оплату',
#                                     callback_data='credit_mutation'))
#     markup.row(InlineKeyboardButton(text='⬅Назад',
#                                     callback_data='cancel'))
#     return markup
#
#
# async def base_change_keyboard(db_dishes):
#     markup = InlineKeyboardMarkup(row_width=1)
#     for dish in db_dishes:
#         text_button = f'{dish.name}: {dish.price} грн.'
#         markup.insert(InlineKeyboardButton(text=text_button, callback_data=f'mutation{dish.name}'))
#     markup.row(InlineKeyboardButton(text='Добавить блюдо в меню', callback_data='new_item'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def mutation_keyboard():
#     markup = InlineKeyboardMarkup(row_width=1)
#     markup.row(InlineKeyboardButton(text='Изменить наименование', callback_data='name'))
#     markup.row(InlineKeyboardButton(text='Изменить цену', callback_data='price'))
#     markup.row(InlineKeyboardButton(text='Удалить', callback_data='delete'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def credit_mutation_abc_keyboard(customers: dict):
#     markup = InlineKeyboardMarkup(row_width=2)
#     for l in sorted(list(customers.keys())):
#         markup.insert(InlineKeyboardButton(text=l, callback_data=f'letter{l}'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup
#
#
# async def credit_names_keyboard(customers: dict):
#     markup = InlineKeyboardMarkup(row_width=1)
#     for k, v in customers.items():
#         markup.insert(InlineKeyboardButton(text=v.pseudonym, callback_data=f'push{v.pseudonym}'))
#     markup.row(InlineKeyboardButton(text='⬅Назад', callback_data='cancel'))
#     return markup

async def invoice_keyboard(url, text):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text=text, url=url))
    return markup


async def cancel_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.row(KeyboardButton(text='⬅Назад'))
    return markup

