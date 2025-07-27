
from aiogram import Router
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command
from database.db import get_all_properties
import json

router = Router()

@router.message(Command("list"))
async def list_properties(message: Message):
    properties = get_all_properties()
    if not properties:
        await message.answer("🔍 Объекты не найдены.")
        return

    for prop in properties:
        text = (
            f"🏷 <b>{prop['title']}</b>
"
            f"📍 Адрес: {prop['address']}
"
            f"💰 Цена: {prop['price']} сомони
"
            f"🛏 Комнат: {prop['rooms']}
"
            f"📐 Площадь: {prop['area']} м²
"
            f"📞 Контакт: {prop['contact']}"
        )
        photos = json.loads(prop["photos"])
        if photos:
            await message.bot.send_photo(chat_id=message.chat.id, photo=photos[0], caption=text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StateFilter
from states.search_property import SearchProperty
from aiogram import F
from database.db import search_properties

@router.message(Command("search"))
async def start_search(message: Message, state: FSMContext):
    await message.answer("Введите район или часть адреса (например, 'Сино' или 'улица Ленина'):")
    await state.set_state(SearchProperty.waiting_for_address)

@router.message(StateFilter(SearchProperty.waiting_for_address))
async def search_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Минимальная цена? (только число, например: 500)")
    await state.set_state(SearchProperty.waiting_for_min_price)

@router.message(StateFilter(SearchProperty.waiting_for_min_price))
async def search_min_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число.")
        return
    await state.update_data(min_price=int(message.text))
    await message.answer("Максимальная цена? (только число, например: 2000)")
    await state.set_state(SearchProperty.waiting_for_max_price)

@router.message(StateFilter(SearchProperty.waiting_for_max_price))
async def search_max_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число.")
        return
    await state.update_data(max_price=int(message.text))
    await message.answer("Количество комнат? (например: 1, 2, 3):")
    await state.set_state(SearchProperty.waiting_for_rooms)

@router.message(StateFilter(SearchProperty.waiting_for_rooms))
async def search_rooms(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число.")
        return
    await state.update_data(rooms=int(message.text))
    data = await state.get_data()
    results = search_properties(
        address=data['address'],
        min_price=data['min_price'],
        max_price=data['max_price'],
        rooms=data['rooms']
    )
    if not results:
        await message.answer("По вашему запросу ничего не найдено.")
    else:
        for prop in results:
            text = (
                f"🏷 <b>{prop['title']}</b>
"
                f"📍 Адрес: {prop['address']}
"
                f"💰 Цена: {prop['price']} сомони
"
                f"🛏 Комнат: {prop['rooms']}
"
                f"📐 Площадь: {prop['area']} м²
"
                f"📞 Контакт: {prop['contact']}"
            )
            photos = json.loads(prop["photos"])
            if photos:
                await message.bot.send_photo(chat_id=message.chat.id, photo=photos[0], caption=text, parse_mode="HTML")
            else:
                await message.answer(text, parse_mode="HTML")
    await state.clear()

@router.message(F.text == "🔍 Поиск объектов")
async def search_button(message: Message, state: FSMContext):
    await start_search(message, state)

@router.message(F.text == "📋 Все объекты")
async def list_button(message: Message):
    await list_properties(message)

@router.message(F.text == "📞 Связаться с агентом")
async def contact_button(message: Message):
    await message.answer("📞 Телефон агента: +992 900 00 00 00")

from aiogram.types import CallbackQuery
from keyboards.favorites import get_fav_button
from database.db import add_to_favorites, get_favorites
from aiogram.utils.markdown import hbold

@router.callback_query(F.data.startswith("fav_"))
async def handle_add_to_favorites(callback: CallbackQuery):
    property_id = int(callback.data.split("_")[1])
    add_to_favorites(callback.from_user.id, property_id)
    await callback.answer("Добавлено в избранное!", show_alert=True)

@router.message(Command("fav"))
async def show_favorites(message: Message):
    favorites = get_favorites(message.from_user.id)
    if not favorites:
        await message.answer("⭐ У вас пока нет избранных объектов.")
        return

    for prop in favorites:
        text = (
            f"🏷 <b>{prop['title']}</b>
"
            f"📍 Адрес: {prop['address']}
"
            f"💰 Цена: {prop['price']} сомони
"
            f"🛏 Комнат: {prop['rooms']}
"
            f"📐 Площадь: {prop['area']} м²
"
            f"📞 Контакт: {prop['contact']}"
        )
        photos = json.loads(prop["photos"])
        if photos:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=photos[0],
                caption=text,
                parse_mode="HTML"
            )
        else:
            await message.answer(text, parse_mode="HTML")

from keyboards.sorting import sort_keyboard
from database.db import get_all_properties
from aiogram.types import CallbackQuery

@router.message(Command("sort"))
async def sort_menu(message: Message):
    await message.answer("Выберите способ сортировки:", reply_markup=sort_keyboard)

@router.callback_query(F.data.startswith("sort_"))
async def handle_sorting(callback: CallbackQuery):
    sort_type = callback.data.replace("sort_", "")
    properties = get_all_properties(sort_type)

    if not properties:
        await callback.message.answer("Объекты не найдены.")
    else:
        for prop in properties:
            text = (
                f"🏷 <b>{prop['title']}</b>
"
                f"📍 Адрес: {prop['address']}
"
                f"💰 Цена: {prop['price']} сомони
"
                f"🛏 Комнат: {prop['rooms']}
"
                f"📐 Площадь: {prop['area']} м²
"
                f"📞 Контакт: {prop['contact']}"
            )
            photos = json.loads(prop["photos"])
            if photos:
                await callback.message.bot.send_photo(
                    chat_id=callback.from_user.id,
                    photo=photos[0],
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer(text, parse_mode="HTML")

    await callback.answer()
