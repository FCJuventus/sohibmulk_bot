
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    menu = get_main_menu(message.from_user.id)
    await message.answer("👋 Добро пожаловать! Выберите действие из меню ниже:", reply_markup=menu)
