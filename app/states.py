from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    service_type = State()
    target_content = State()
    content_info = State()
    game_nickname = State()
    deadline = State()
    priority_factors = State()
    details = State()
