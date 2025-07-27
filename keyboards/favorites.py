
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_fav_button(property_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav_{property_id}")]
    ])
