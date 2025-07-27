
from database.db import subscribe_user

@router.message(Command("subscribe"))
async def ask_subscription_filters(message: Message, state: FSMContext):
    await state.set_state(FSMClient.subscribe_price)
    await message.answer("💰 Введите максимальную цену (например: 200000):")

@router.message(FSMClient.subscribe_price)
async def subscribe_price(message: Message, state: FSMContext):
    await state.update_data(max_price=int(message.text))
    await state.set_state(FSMClient.subscribe_rooms)
    await message.answer("🛏 Введите количество комнат:")

@router.message(FSMClient.subscribe_rooms)
async def subscribe_rooms(message: Message, state: FSMContext):
    await state.update_data(rooms=int(message.text))
    await state.set_state(FSMClient.subscribe_area)
    await message.answer("📍 Введите район (по желанию):")

@router.message(FSMClient.subscribe_area)
async def subscribe_area(message: Message, state: FSMContext):
    data = await state.update_data(area_hint=message.text)
    subscribe_user(user_id=message.from_user.id, **data)
    await message.answer("🔔 Подписка успешно оформлена! Мы уведомим вас, когда появятся подходящие объекты.")
    await state.clear()

@router.message(Command("language"))
async def choose_language(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English"), KeyboardButton(text="🇹🇯 Тоҷикӣ")]
        ],
        resize_keyboard=True
    )
    from utils.localization import get_text
    await message.answer(get_text(message.from_user.id, "choose_language"), reply_markup=kb)

@router.message(F.text.in_(["🇷🇺 Русский", "🇬🇧 English", "🇹🇯 Тоҷикӣ"]))
async def set_language(message: Message):
    from database.db import set_user_language
    lang_map = {
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
        "🇹🇯 Тоҷикӣ": "tj"
    }
    lang = lang_map[message.text]
    set_user_language(message.from_user.id, lang)
    from utils.localization import get_text
    await message.answer(get_text(message.from_user.id, "language_saved"), reply_markup=ReplyKeyboardRemove())
