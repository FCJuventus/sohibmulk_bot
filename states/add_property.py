
from aiogram.fsm.state import State, StatesGroup

class AddProperty(StatesGroup):
    waiting_for_title = State()
    waiting_for_address = State()
    waiting_for_price = State()
    waiting_for_rooms = State()
    waiting_for_area = State()
    waiting_for_photos = State()
    waiting_for_contact = State()
    confirmation = State()
