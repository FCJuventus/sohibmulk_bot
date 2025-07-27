from aiogram import types

async def help_command_handler(message: types.Message):
    await message.answer("🆘 Список доступных команд:
/start
/help
/admin")