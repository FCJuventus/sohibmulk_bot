from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я бот Sohibmulk, чем могу помочь?")