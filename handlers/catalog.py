from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import ADMIN_IDS
from database import (
    add_episode,
    create_anime,
    get_anime_by_code,
    get_episodes,
    list_anime,
)
from keyboards import episode_picker

router = Router()


class CatalogState(StatesGroup):
    anime_code = State()
    anime_title = State()
    anime_description = State()
    anime_poster = State()
    episode_code = State()
    episode_number = State()
    episode_media = State()
    user_code = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(F.data == "catalog:add_anime")
async def begin_add_anime(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    await state.clear()
    await state.set_state(CatalogState.anime_code)
    await call.message.answer("Anime uchun noyob kod yuboring (masalan, NARUTO).")
    await call.answer()


@router.message(CatalogState.anime_code)
async def receive_anime_code(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    code = (message.text or "").strip().upper()
    if not code or len(code) > 20 or not code.replace("_", "").isalnum():
        await message.answer("Kod 1–20 belgidan iborat bo‘lsin; harf, raqam va _ ishlating.")
        return
    if await get_anime_by_code(code):
        await message.answer("Bu kod allaqachon ishlatilgan. Boshqa kod kiriting.")
        return
    await state.update_data(anime_code=code)
    await state.set_state(CatalogState.anime_title)
    await message.answer("Anime nomini yuboring.")


@router.message(CatalogState.anime_title)
async def receive_anime_title(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    title = (message.text or "").strip()
    if not title:
        await message.answer("Anime nomi bo‘sh bo‘lmasin.")
        return
    await state.update_data(anime_title=title[:200])
    await state.set_state(CatalogState.anime_description)
    await message.answer("Tavsif yuboring (bo‘lmasa - yuboring).")


@router.message(CatalogState.anime_description)
async def receive_anime_description(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    description = (message.text or "").strip()
    if not description:
        await message.answer("Tavsif matn yoki - bo‘lishi kerak.")
        return
    await state.update_data(anime_description="" if description == "-" else description[:3000])
    await state.set_state(CatalogState.anime_poster)
    await message.answer("Poster rasmini yuboring yoki - deb yozib o‘tkazing.")


@router.message(CatalogState.anime_poster)
async def receive_anime_poster(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.photo:
        poster_file_id = message.photo[-1].file_id
    elif message.text and message.text.strip() == "-":
        poster_file_id = None
    else:
        await message.answer("Poster rasmi yoki o‘tkazish uchun - yuboring.")
        return

    data = await state.get_data()
    await create_anime(
        data["anime_code"],
        data["anime_title"],
        data["anime_description"],
        poster_file_id,
    )
    await state.clear()
    await message.answer(f"��� Anime katalogga qo‘shildi. Kodi: {data['anime_code']}")


@router.callback_query(F.data == "catalog:add_episode")
async def begin_add_episode(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    await state.clear()
    await state.set_state(CatalogState.episode_code)
    await call.message.answer("Qism qo‘shiladigan anime kodini yuboring.")
    await call.answer()


@router.message(CatalogState.episode_code)
async def receive_episode_code(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    code = (message.text or "").strip().upper()
    anime = await get_anime_by_code(code) if code else None
    if not anime:
        await message.answer("Anime kodi topilmadi. Avval anime qo‘shing yoki kodni tekshiring.")
        return
    await state.update_data(episode_code=code)
    await state.set_state(CatalogState.episode_number)
    await message.answer(f"{anime[1]} tanlandi. Qism raqamini yuboring (masalan, 1).")


@router.message(CatalogState.episode_number)
async def receive_episode_number(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    episode_no = (message.text or "").strip()
    if not episode_no or len(episode_no) > 15:
        await message.answer("Qism raqamini 1–15 belgida yuboring.")
        return
    await state.update_data(episode_no=episode_no)
    await state.set_state(CatalogState.episode_media)
    await message.answer("Qism videosini yoki hujjat/video faylini yuboring.")


@router.message(CatalogState.episode_media)
async def receive_episode_media(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if message.video:
        media_type, media_value = "video", message.video.file_id
    elif message.document:
        media_type, media_value = "document", message.document.file_id
    else:
        await message.answer("Video yoki hujjat ko‘rinishidagi media yuboring.")
        return
    data = await state.get_data()
    await add_episode(data["episode_code"], data["episode_no"], media_type, media_value)
    await state.clear()
    await message.answer(
        f"✅ {data['episode_code']} anime katalogiga {data['episode_no']}-qism qo‘shildi."
    )


@router.callback_query(F.data == "catalog:list")
async def show_catalog_list(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    anime_items = await list_anime()
    if not anime_items:
        await call.message.answer("Katalog hozircha bo‘sh.")
    else:
        lines = [f"• <b>{title}</b> — kod: <code>{code}</code>" for code, title in anime_items[:100]]
        await call.message.answer("📚 <b>Anime katalogi:</b>\n" + "\n".join(lines))
    await call.answer()


@router.message(F.text == "🎟 Kod orqali topish")
async def begin_code_search(message: Message, state: FSMContext):
    await state.set_state(CatalogState.user_code)
    await message.answer("Anime kodini yuboring.")


@router.message(CatalogState.user_code)
async def find_by_code(message: Message, state: FSMContext):
    code = (message.text or "").strip().upper()
    anime = await get_anime_by_code(code) if code else None
    await state.clear()
    if not anime:
        await message.answer("Bunday kodli anime topilmadi. Kodni tekshirib qayta urinib ko‘ring.")
        return
    _code, title, description, poster_file_id = anime
    episodes = await get_episodes(_code)
    caption = f"🎌 <b>{title}</b>\n\n{description or 'Tavsif mavjud emas.'}"
    if poster_file_id:
        await message.answer_photo(poster_file_id, caption=caption)
    else:
        await message.answer(caption)
    if episodes:
        await message.answer("Ko‘rish uchun qismni tanlang:", reply_markup=episode_picker(_code, episodes))
    else:
        await message.answer("Bu anime uchun qismlar hali qo‘shilmagan.")


@router.callback_query(F.data.startswith("catalog:watch:"))
async def send_episode(call: CallbackQuery):
    parts = call.data.split(":", 3)
    if len(parts) != 4:
        await call.answer("Qism topilmadi.", show_alert=True)
        return
    _prefix, _action, code, episode_no = parts
    episodes = await get_episodes(code)
    episode = next((item for item in episodes if item[0] == episode_no), None)
    if not episode:
        await call.answer("Bu qism topilmadi.", show_alert=True)
        return
    _episode_no, media_type, media_value = episode
    if media_type == "video":
        await call.message.answer_video(media_value, caption=f"🎬 {code} — {episode_no}-qism")
    elif media_type == "document":
        await call.message.answer_document(media_value, caption=f"🎬 {code} — {episode_no}-qism")
    else:
        await call.answer("Media turi qo‘llab-quvvatlanmaydi.", show_alert=True)
        return
    await call.answer()
