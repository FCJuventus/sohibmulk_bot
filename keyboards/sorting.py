
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

sort_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="💵 Цена ↑", callback_data="sort_price_asc"),
        InlineKeyboardButton(text="💰 Цена ↓", callback_data="sort_price_desc")
    ],
    [
        InlineKeyboardButton(text="🆕 Новые", callback_data="sort_new"),
        InlineKeyboardButton(text="🧓 Старые", callback_data="sort_old")
    ]
])
