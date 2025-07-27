
from aiogram.fsm.state import State, StatesGroup

class DeleteProperty(StatesGroup):
    waiting_for_id = State()
    confirmation = State()
