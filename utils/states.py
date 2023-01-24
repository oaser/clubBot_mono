from aiogram.dispatcher.filters.state import StatesGroup, State


class Payment(StatesGroup):
    periods = State()
    checkout = State()
    info = State()


class MainMenu(StatesGroup):
    full_reg = State()
    half_reg = State()
    no_reg = State()


class RegMenu(StatesGroup):
    reg_name = State()
    reg_age = State()
    reg_location = State()
    reg_approve = State()


class AdminMenu(StatesGroup):
    initial = State()
    name = State()
    surname = State()


