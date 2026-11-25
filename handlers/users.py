from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import main_menu, anime_results, anime_actions
from database import add_user, toggle_favorite, get_favorites
from services import search_anime, get_anime
from config import ADMIN_IDS

router = Router()

class SearchState(StatesGroup):
    waiting_query = State()

def format_anime(data):
    title = data.get("title") or "Noma’lum"
    title_jp = data.get("title_japanese") or "—"
    synopsis = data.get("synopsis") or "Tavsif mavjud emas."
    synopsis = synopsis[:850] + ("…" if len(synopsis) > 850 else "")
    genres = ", ".join(g.get("name", "") for g in data.get("genres", [])) or "—"
    year = data.get("year") or (data.get("aired") or {}).get("prop", {}).get("from", {}).get("year") or "—"
    score = data.get("score") or "—"
    episodes = data.get("episodes") or "Noma’lum"
    status = data.get("status") or "—"
    return (f"🎌 <b>{title}</b>\n"
            f"🇯🇵 Yaponcha nomi: {title_jp}\n"
            f"📅 Yil: {year}\n⭐ Reyting: {score}\n"
            f"🎞 Qismlar: {episodes}\n📌 Holati: {status}\n"
            f"🏷 Janrlar: {genres}\n\n{synopsis}")

@router.message(F.text == "/start")
async def start(message: Message):
    await add_user(message.from_user.id)
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 🎌\n"
        "Anime olamiga xush kelibsiz. Anime qidirish tugmasini bosing.",
        reply_markup=main_menu(message.from_user.id in ADMIN_IDS)
    )

@router.message(F.text == "🛠 Admin panel")
async def open_admin_menu(message: Message):
    if message.from_user.id in ADMIN_IDS:
        from keyboards import admin_menu
        await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu(), parse_mode="HTML")

@router.message(F.text == "🔎 Anime qidirish")
async def ask_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await message.answer("🔎 Anime nomini yuboring. O‘zbekcha, inglizcha yoki yaponcha nom bilan qidirishingiz mumkin.")

@router.message(SearchState.waiting_query)
async def do_search(message: Message, state: FSMContext):
    query = (message.text or "").strip()
    if len(query) < 2:
        await message.answer("Kamida 2 ta harf yuboring.")
        return
    await state.clear()
    try:
        results = await search_anime(query)
        if not results:
            await message.answer("😕 Hech narsa topilmadi. Boshqa nom bilan urinib ko‘ring.")
            return
        await message.answer("🔎 Topilgan animelar:", reply_markup=anime_results(results))
    except Exception as exc:
        await message.answer(f"Qidiruvda xatolik: {str(exc)[:250]}")

@router.callback_query(F.data.startswith("anime:"))
async def show_anime(call: CallbackQuery):
    anime_id = int(call.data.split(":")[1])
    try:
        data = await get_anime(anime_id)
        if not data:
            await call.answer("Anime topilmadi.", show_alert=True)
            return
        caption = format_anime(data)
        image = ((data.get("images") or {}).get("jpg") or {}).get("large_image_url")
        if image:
            await call.message.answer_photo(image, caption=caption, reply_markup=anime_actions(anime_id), parse_mode="HTML")
        else:
            await call.message.answer(caption, reply_markup=anime_actions(anime_id), parse_mode="HTML")
        await call.answer()
    except Exception as exc:
        await call.answer("Ma’lumotni olishda xatolik yuz berdi.", show_alert=True)

@router.callback_query(F.data.startswith("fav:"))
async def favorite(call: CallbackQuery):
    anime_id = int(call.data.split(":")[1])
    try:
        data = await get_anime(anime_id)
        title = data.get("title", f"Anime {anime_id}") if data else f"Anime {anime_id}"
        added = await toggle_favorite(call.from_user.id, anime_id, title)
        await call.answer("Sevimlilarga qo‘shildi ❤️" if added else "Sevimlilardan olib tashlandi.", show_alert=True)
    except Exception:
        await call.answer("Xatolik yuz berdi.", show_alert=True)

@router.message(F.text == "❤️ Sevimlilar")
async def favorites(message: Message):
    rows = await get_favorites(message.from_user.id)
    if not rows:
        await message.answer("Hozircha sevimli animelaringiz yo‘q.")
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❤️ {title[:55]}", callback_data=f"anime:{anime_id}")]
        for anime_id, title in rows[:50]
    ])
    await message.answer("Sevimli animelaringiz:", reply_markup=kb)

@router.message(F.text == "🔥 Top animelar")
async def top_anime(message: Message):
    try:
        results = await search_anime("one piece")
        if results:
            await message.answer("🔥 Mashhur animelar katalogi:", reply_markup=anime_results(results))
        else:
            await message.answer("Hozircha ro‘yxatni yuklab bo‘lmadi.")
    except Exception:
        await message.answer("Xizmat vaqtincha ishlamayapti. Keyinroq urinib ko‘ring.")

@router.message(F.text == "ℹ️ Yordam")
async def help_message(message: Message):
    await message.answer(
        "ℹ️ <b>Anime Bot yordam</b>\n"
        "🔎 Anime qidirish — nom orqali anime topish.\n"
        "❤️ Sevimlilar — yoqtirgan animelaringizni saqlash.\n"
        "Anime ma’lumotlari Jikan API orqali olinadi.",
        parse_mode="HTML"
    )
