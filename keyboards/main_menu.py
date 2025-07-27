
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS

def get_main_menu(user_id: int):
    buttons = [
        [KeyboardButton(text="🔍 Поиск объектов")],
        [KeyboardButton(text="📋 Все объекты")],
        [KeyboardButton(text="📞 Связаться с агентом")]
    ]

    if user_id in ADMIN_IDS:
        buttons.extend([
            [KeyboardButton(text="➕ Добавить объект")],
            [KeyboardButton(text="🗑 Удалить объект")],
            [KeyboardButton(text="📝 Редактировать объект")]
        ])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
