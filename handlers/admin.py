from utils.notifier import notify_subscribers

from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states.add_property import AddProperty
from config import ADMIN_IDS
import json

router = Router()

# Начало добавления объекта
@router.message(Command("add"), F.from_user.id.in_(ADMIN_IDS))
async def start_add_property(message: Message, state: FSMContext):
    await message.answer("Введите название или тип объекта (например, 2-комнатная квартира):")
    await state.set_state(AddProperty.waiting_for_title)

@router.message(StateFilter(AddProperty.waiting_for_title))
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите адрес объекта:")
    await state.set_state(AddProperty.waiting_for_address)

@router.message(StateFilter(AddProperty.waiting_for_address))
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите цену (только число):")
    await state.set_state(AddProperty.waiting_for_price)

@router.message(StateFilter(AddProperty.waiting_for_price))
async def process_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите только число.")
        return
    await state.update_data(price=int(message.text))
    await message.answer("Введите количество комнат:")
    await state.set_state(AddProperty.waiting_for_rooms)

@router.message(StateFilter(AddProperty.waiting_for_rooms))
async def process_rooms(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите только число.")
        return
    await state.update_data(rooms=int(message.text))
    await message.answer("Введите площадь в м²:")
    await state.set_state(AddProperty.waiting_for_area)

@router.message(StateFilter(AddProperty.waiting_for_area))
async def process_area(message: Message, state: FSMContext):
    try:
        area = float(message.text)
        await state.update_data(area=area)
        await message.answer("Загрузите до 5 фото объекта одним сообщением:")
        await state.set_state(AddProperty.waiting_for_photos)
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 55.6)")

@router.message(StateFilter(AddProperty.waiting_for_photos))
async def process_photos(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото.")
        return
    photos = [p.file_id for p in message.photo[-1:]]  # Берём только самое качественное фото
    await state.update_data(photos=photos)
    await message.answer("Введите контактный номер (или имя + номер):")
    await state.set_state(AddProperty.waiting_for_contact)

@router.message(StateFilter(AddProperty.waiting_for_contact))
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    text = (
        f"Проверьте информацию:

"
        f"🏷 Название: {data['title']}
"
        f"📍 Адрес: {data['address']}
"
        f"💰 Цена: {data['price']} сомони
"
        f"🛏 Комнат: {data['rooms']}
"
        f"📐 Площадь: {data['area']} м²
"
        f"📞 Контакт: {data['contact']}

"
        "Подтвердите добавление? (да/нет)"
    )
    await state.set_state(AddProperty.confirmation)
    await message.answer(text)

@router.message(StateFilter(AddProperty.confirmation))
async def confirm_property(message: Message, state: FSMContext):
    if message.text.lower() != "да":
        await message.answer("Добавление отменено.")
        await state.clear()
        return

    data = await state.get_data()
    data["owner_id"] = message.from_user.id
    from database.db import add_property_to_db
    add_property_to_db(data)
    await message.answer("✅ Объект добавлен в базу!")
    await state.clear()

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StateFilter
from aiogram import F
from states.delete_property import DeleteProperty
from database.db import get_all_properties, delete_property_by_id
import json

@router.message(Command("delete"), F.from_user.id.in_(ADMIN_IDS))
async def start_delete(message: Message, state: FSMContext):
    properties = get_all_properties()
    if not properties:
        await message.answer("Нет объектов для удаления.")
        return

    text = "🗑 <b>Список объектов:</b>

"
    for prop in properties:
        text += f"ID: {prop['id']} | {prop['title']} — {prop['price']} сомони
"

    await message.answer(text + "
Введите ID объекта, который нужно удалить:", parse_mode="HTML")
    await state.set_state(DeleteProperty.waiting_for_id)

@router.message(StateFilter(DeleteProperty.waiting_for_id))
async def ask_confirmation(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите числовой ID.")
        return
    await state.update_data(delete_id=int(message.text))
    await message.answer(f"Вы уверены, что хотите удалить объект с ID {message.text}? (да/нет)")
    await state.set_state(DeleteProperty.confirmation)

@router.message(StateFilter(DeleteProperty.confirmation))
async def confirm_delete(message: Message, state: FSMContext):
    if message.text.lower() != "да":
        await message.answer("Удаление отменено.")
        await state.clear()
        return

    data = await state.get_data()
    success = delete_property_by_id(data["delete_id"])
    if success:
        await message.answer("✅ Объект успешно удалён.")
    else:
        await message.answer("❌ Ошибка: объект с таким ID не найден.")
    await state.clear()

from states.edit_property import EditProperty
from database.db import get_all_properties, edit_property_field

@router.message(Command("edit"), F.from_user.id.in_(ADMIN_IDS))
async def start_edit(message: Message, state: FSMContext):
    properties = get_all_properties()
    if not properties:
        await message.answer("Нет объектов для редактирования.")
        return

    text = "📝 <b>Список объектов:</b>

"
    for prop in properties:
        text += f"ID: {prop['id']} | {prop['title']} — {prop['price']} сомони
"

    await message.answer(text + "
Введите ID объекта, который хотите изменить:", parse_mode="HTML")
    await state.set_state(EditProperty.waiting_for_id)

@router.message(StateFilter(EditProperty.waiting_for_id))
async def choose_field(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите числовой ID.")
        return
    await state.update_data(edit_id=int(message.text))
    await message.answer(
        "Какое поле вы хотите изменить?
"
        "Допустимые варианты: title, address, price, rooms, area, contact"
    )
    await state.set_state(EditProperty.waiting_for_field)

@router.message(StateFilter(EditProperty.waiting_for_field))
async def enter_value(message: Message, state: FSMContext):
    field = message.text.lower()
    allowed_fields = ['title', 'address', 'price', 'rooms', 'area', 'contact']
    if field not in allowed_fields:
        await message.answer("Недопустимое поле. Попробуйте снова.")
        return
    await state.update_data(edit_field=field)
    await message.answer(f"Введите новое значение для поля {field}:")
    await state.set_state(EditProperty.waiting_for_value)

@router.message(StateFilter(EditProperty.waiting_for_value))
async def save_edited_value(message: Message, state: FSMContext):
    data = await state.get_data()
    success = edit_property_field(data["edit_id"], data["edit_field"], message.text)
    if success:
        await message.answer("✅ Объект успешно обновлён.")
    else:
        await message.answer("❌ Объект не найден или поле не обновлено.")
    await state.clear()

@router.message(F.text == "➕ Добавить объект", F.from_user.id.in_(ADMIN_IDS))
async def add_button(message: Message, state: FSMContext):
    await start_add_property(message, state)

@router.message(F.text == "🗑 Удалить объект", F.from_user.id.in_(ADMIN_IDS))
async def delete_button(message: Message, state: FSMContext):
    await start_delete(message, state)

@router.message(F.text == "📝 Редактировать объект", F.from_user.id.in_(ADMIN_IDS))
async def edit_button(message: Message, state: FSMContext):
    await start_edit(message, state)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.export import fetch_all_properties, generate_excel, generate_pdf
from aiogram import F
import os

export_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📄 PDF", callback_data="export_pdf")],
    [InlineKeyboardButton(text="📊 Excel", callback_data="export_excel")]
])

@router.message(Command("export"), F.from_user.id.in_(ADMIN_IDS))
async def export_prompt(message: Message):
    await message.answer("Выберите формат экспорта:", reply_markup=export_keyboard)

@router.callback_query(F.data == "export_pdf", F.from_user.id.in_(ADMIN_IDS))
async def export_pdf(callback: CallbackQuery):
    props = fetch_all_properties()
    path = generate_pdf(props)
    with open(path, "rb") as f:
        await callback.message.answer_document(f, caption="📄 Экспорт в PDF завершён.")
    await callback.answer()

@router.callback_query(F.data == "export_excel", F.from_user.id.in_(ADMIN_IDS))
async def export_excel(callback: CallbackQuery):
    props = fetch_all_properties()
    path = generate_excel(props)
    with open(path, "rb") as f:
        await callback.message.answer_document(f, caption="📊 Экспорт в Excel завершён.")
    await callback.answer()

from database.db import get_properties_by_owner
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.message(Command("my"), F.from_user.id.in_(ADMIN_IDS))
async def my_objects(message: Message):
    props = get_properties_by_owner(message.from_user.id)
    if not props:
        await message.answer("У вас пока нет добавленных объектов.")
        return

    await message.answer(f"📂 Всего ваших объектов: {len(props)}")

    for prop in props:
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
            f"📞 Контакт: {prop['contact']}
"
            f"🆔 ID: {prop['id']}"
        )
        photos = json.loads(prop["photos"])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏ Редактировать", callback_data=f"edit_{prop['id']}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{prop['id']}"),InlineKeyboardButton(text="📦 Архивировать", callback_data=f"archive_{prop['id']}")]
        ])
        if photos:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=photos[0],
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

from utils.importer import import_from_excel
from aiogram.types import FSInputFile
import os

@router.message(Command("import"), F.from_user.id.in_(ADMIN_IDS))
async def prompt_import(message: Message):
    await message.answer("📎 Отправьте Excel-файл (.xlsx) с объектами недвижимости.")

@router.message(F.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", F.from_user.id.in_(ADMIN_IDS))
async def handle_import_file(message: Message):
    file = await message.bot.get_file(message.document.file_id)
    path = f"media/import_{message.from_user.id}.xlsx"
    await message.bot.download_file(file.file_path, destination=path)

    count = import_from_excel(path, owner_id=message.from_user.id)
    await message.answer(f"✅ Импорт завершён. Добавлено объектов: {count}")

@router.callback_query(F.data.startswith("archive_"), F.from_user.id.in_(ADMIN_IDS))
async def archive_property(callback: CallbackQuery):
    prop_id = callback.data.split("_")[1]
    conn = sqlite3.connect("realty.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE properties SET status = 'archived' WHERE id = ?", (prop_id,))
    conn.commit()
    conn.close()
    await callback.message.edit_caption("<i>📦 Объект перемещён в архив</i>", parse_mode="HTML")
    await callback.answer("Объект архивирован.")

@router.message(FSMAdmin.location, F.location)
async def get_location(message: Message, state: FSMContext):
    await state.update_data(latitude=message.location.latitude)
    await state.update_data(longitude=message.location.longitude)
    await state.set_state(FSMAdmin.confirm)
    await message.answer("✅ Локация получена. Подтвердите добавление объекта.")
