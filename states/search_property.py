
from aiogram.fsm.state import State, StatesGroup

class SearchProperty(StatesGroup):
    waiting_for_address = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    waiting_for_rooms = State()
