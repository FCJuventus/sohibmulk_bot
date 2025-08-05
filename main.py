import logging  # <- ДОБАВЬ ЭТУ СТРОКУ
logging.basicConfig(level=logging.INFO)  # <- И ЭТУ СТРОКУ

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import asyncio
import os

from handlers import start_router, user_router, admin_router, help_router
from database.db import auto_archive_old_properties

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    auto_archive_old_properties()  # автоархивация устаревших объектов
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(help_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())