from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    customer_name = State()
    service_type = State()
    game_nickname = State()
    contact = State()
    deadline = State()
    details = State()
