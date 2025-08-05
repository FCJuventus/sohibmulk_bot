from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

start_router = Router()

from keyboards.main_menu import main_menu_kb  # ← твоя клавиатура

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот Sohibmulk. Чем могу помочь?",
        reply_markup=main_menu_kb  # ← добавить клавиатуру
    )