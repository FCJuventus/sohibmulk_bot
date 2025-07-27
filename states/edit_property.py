
from aiogram.fsm.state import State, StatesGroup

class EditProperty(StatesGroup):
    waiting_for_id = State()
    waiting_for_field = State()
    waiting_for_value = State()
