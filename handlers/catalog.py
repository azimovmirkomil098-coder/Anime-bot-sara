from aiogram import Router, F
from html import escape
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from keyboards import required_subscription_keyboard, anime_episode_keyboard, main_menu
from database import (create_anime, get_anime_by_code, list_anime, add_episode,
                      get_episodes, get_required_channels)

router = Router()
def admin(uid): return uid in ADMIN_IDS

async def is_subscribed(bot, user_id):
    channels = await get_required_channels()
    for chat_id, _title, _link in channels:
        try:
            member = await bot.get_chat_member(int(chat_id), user_id)
            if member.status in ("left", "kicked") or (member.status == "restricted" and not getattr(member, "is_member", False)):
                return False, channels
        except Exception:
            return False, channels
    return True, channels

async def require_subscription(message_or_call, anime_code=None):
    ok, channels = await is_subscribed(message_or_call.bot, message_or_call.from_user.id)
    if ok: return True
    text = "🔒 <b>Animeni ko‘rish uchun avval quyidagi kanallarga obuna bo‘ling:</b>"
    markup = required_subscription_keyboard(channels, anime_code)
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await message_or_call.answer("Avval barcha majburiy kanallarga obuna bo‘ling.", show_alert=True)
        await message_or_call.message.answer(text, reply_markup=markup, parse_mode="HTML")
    return False

async def show_catalog_anime(message: Message, code: str):
    anime = await get_anime_by_code(code)
    if not anime:
        await message.answer("Bu kod bo‘yicha anime topilmadi.")
        return
    eps = await get_episodes(code)
    _code,title,description,poster,genre,year,language = anime
    caption = (f"🎌 <b>{escape(title)}</b>\n🔑 Kod: <code>{escape(_code)}</code>\n"
               f"🏷 Janr: {escape(genre or 'Ko‘rsatilmagan')}\n📅 Yil: {escape(year or 'Ko‘rsatilmagan')}\n"
               f"🌐 Til: {escape(language or 'Ko‘rsatilmagan')}\n🎬 Qismlar: {len(eps)} ta\n\n"
               f"{escape((description or 'Tavsif mavjud emas.')[:650])}")
    if poster:
        await message.answer_photo(poster, caption=caption, parse_mode="HTML")
    else:
        await message.answer(caption, parse_mode="HTML")
    if eps:
        await message.answer("Ko‘rmoqchi bo‘lgan qismni tanlang:", reply_markup=anime_episode_keyboard(code, eps))
    else:
        await message.answer("Hozircha bu animega qismlar qo‘shilmagan.")

class UserState(StatesGroup): waiting_code = State()
class CatalogState(StatesGroup):
    anime_title=State(); anime_code=State(); anime_genre=State(); anime_year=State()
    anime_language=State(); anime_description=State(); anime_poster=State()
    episode_code=State(); episode_media=State()

@router.callback_query(F.data == 'catalog:add_anime')
async def add_anime_start(call: CallbackQuery, state: FSMContext):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q', show_alert=True)
    await state.clear(); await state.set_state(CatalogState.anime_title)
    await call.message.answer('Anime nomini yuboring:'); await call.answer()

@router.message(CatalogState.anime_title)
async def anime_title(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    title=(message.text or '').strip()
    if len(title)<2: return await message.answer('Nom kamida 2 ta belgidan iborat bo‘lsin.')
    await state.update_data(title=title); await state.set_state(CatalogState.anime_code)
    await message.answer('Takrorlanmaydigan anime kodini kiriting (masalan: A101):')

@router.message(CatalogState.anime_code)
async def anime_code(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    code=(message.text or '').strip().upper()
    if not code or len(code)>20 or not code.replace('_','').replace('-','').isalnum(): return await message.answer('Kod faqat harf, raqam, _ yoki - dan iborat bo‘lsin.')
    if await get_anime_by_code(code): return await message.answer('Bu kod band. Boshqa kod kiriting:')
    await state.update_data(code=code); await state.set_state(CatalogState.anime_genre)
    await message.answer('Anime janrini kiriting (masalan: Action, Fantasy, Romance).')

@router.message(CatalogState.anime_genre)
async def anime_genre(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    await state.update_data(genre=(message.text or '').strip()); await state.set_state(CatalogState.anime_year)
    await message.answer('Chiqqan yilini kiriting (masalan: 2024):')

@router.message(CatalogState.anime_year)
async def anime_year(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    year=(message.text or '').strip()
    if not year.isdigit() or len(year)!=4: return await message.answer('Yilni 4 xonali son bilan kiriting, masalan 2024:')
    await state.update_data(year=year); await state.set_state(CatalogState.anime_language)
    await message.answer('Anime qaysi tilda? (masalan: O‘zbekcha, Ruscha, Yaponcha):')

@router.message(CatalogState.anime_language)
async def anime_language(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    await state.update_data(language=(message.text or '').strip()); await state.set_state(CatalogState.anime_description)
    await message.answer('Anime tavsifini yuboring. Kerak bo‘lmasa /skip yozing:')

@router.message(CatalogState.anime_description)
async def anime_description(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    desc='' if message.text=='/skip' else (message.text or '').strip()
    await state.update_data(description=desc); await state.set_state(CatalogState.anime_poster)
    await message.answer('Anime posterini rasm qilib yuboring yoki /skip yozing:')

@router.message(CatalogState.anime_poster)
async def anime_poster(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    if message.text != '/skip' and not message.photo: return await message.answer('Rasm yuboring yoki postersiz davom etish uchun /skip yozing.')
    data=await state.get_data(); poster=message.photo[-1].file_id if message.photo else None
    try: await create_anime(data['code'],data['title'],data['description'],poster,data['genre'],data['year'],data['language'])
    except Exception:
        await message.answer('Anime saqlanmadi. Kod band bo‘lishi mumkin.'); await state.clear(); return
    await state.clear()
    await message.answer(f"✅ Anime qo‘shildi!\n🎌 {data['title']}\n🔑 Kod: <code>{data['code']}</code>\nEndi 🎬 Qism qo‘shish orqali videolarni ketma-ket yuborishingiz mumkin.",parse_mode='HTML')

@router.callback_query(F.data == 'catalog:add_episode')
async def add_episode_start(call: CallbackQuery,state: FSMContext):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    await state.clear(); await state.set_state(CatalogState.episode_code)
    await call.message.answer('Qismlari qo‘shiladigan anime kodini yuboring:'); await call.answer()

@router.message(CatalogState.episode_code)
async def episode_code(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    code=(message.text or '').strip().upper(); anime=await get_anime_by_code(code)
    if not anime: return await message.answer('Bunday kodli anime topilmadi. To‘g‘ri kod kiriting:')
    eps=await get_episodes(code); next_no=max([int(e[0]) for e in eps],default=0)+1
    await state.update_data(code=code,title=anime[1],next_no=next_no); await state.set_state(CatalogState.episode_media)
    await message.answer(f"🎌 {anime[1]}\nEndi videolarni ketma-ket yuboring. Birinchi video avtomatik {next_no}-qism bo‘ladi.\n\nHar video yuborilgach keyingi raqam avtomatik belgilanadi. Tugatish uchun /done yozing.")

@router.message(CatalogState.episode_media)
async def episode_media(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    data=await state.get_data(); no=data['next_no']
    if message.text and message.text.strip().lower() == '/done':
        await state.clear(); return await message.answer('✅ Qismlarni yuklash yakunlandi.', reply_markup=__import__('keyboards').admin_menu())
    if message.video:
        kind='telegram'; value=message.video.file_id
    else:
        value=(message.text or '').strip()
        if not (value.startswith('https://') or value.startswith('http://')):
            return await message.answer(f'{no}-qism videosini yuboring yoki video URL kiriting. Tugatish: /done')
        kind='url'
    try: await add_episode(data['code'],no,kind,value)
    except Exception: return await message.answer('Qismni saqlashda xatolik. Qayta yuboring.')
    await state.update_data(next_no=no+1)
    await message.answer(f"✅ {no}-qism saqlandi.\nKeyingi video {no+1}-qism bo‘ladi. Davom eting yoki /done yozing.")

@router.callback_query(F.data == 'catalog:list')
async def catalog_list(call: CallbackQuery):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    rows=await list_anime()
    if not rows: await call.message.answer('Hozircha anime qo‘shilmagan.')
    else:
        for code,title in rows[:50]:
            anime=await get_anime_by_code(code); eps=await get_episodes(code)
            await call.message.answer(f'🎌 <b>{title}</b>\n🔑 Kod: <code>{code}</code>\n🏷 {anime[4]} | 📅 {anime[5]} | 🌐 {anime[6]}\n🎬 Qismlar: {len(eps)}',parse_mode='HTML',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📢 Kanalga post qilish',callback_data=f'catalog:post:{code}')]]))
    await call.answer()

@router.callback_query(F.data.startswith('catalog:post:'))
async def post_anime_info(call: CallbackQuery):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    code=call.data.split(':',2)[2]; anime=await get_anime_by_code(code)
    if not anime: return await call.answer('Anime topilmadi',show_alert=True)
    from database import get_channels
    channels=await get_channels()
    if not channels: return await call.answer('Avval post kanallarini qo‘shing',show_alert=True)
    me=await call.bot.get_me(); bot_link=f"https://t.me/{me.username}?start=anime_{code}"
    eps=await get_episodes(code)
    caption=(f"🎌 <b>{escape(anime[1])}</b>\n🏷 <b>Janr:</b> {escape(anime[4] or '—')}\n📅 <b>Yili:</b> {escape(anime[5] or '—')}\n"
             f"🌐 <b>Tili:</b> {escape(anime[6] or '—')}\n🎬 <b>Qismlar:</b> {len(eps)} ta\n\n"
             f"{escape((anime[2] or 'Tavsif mavjud emas.')[:650])}")
    markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='▶️ Animeni ko‘rish',url=bot_link)]])
    sent=0
    for cid,_ in channels:
        try:
            if anime[3]: await call.bot.send_photo(cid,anime[3],caption=caption,parse_mode='HTML',reply_markup=markup)
            else: await call.bot.send_message(cid,caption,parse_mode='HTML',reply_markup=markup)
            sent+=1
        except Exception: pass
    await call.message.answer(f'📢 Anime {sent}/{len(channels)} ta kanalga joylandi. Postdagi tugma botga olib o‘tadi.')
    await call.answer()

def browse_keyboard(rows, page=0, page_size=8):
    buttons = []
    start = page * page_size
    for code, title in rows[start:start + page_size]:
        buttons.append([InlineKeyboardButton(text=f"🎌 {title[:52]}", callback_data=f"browse:anime:{code}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"browse:page:{page-1}"))
    if start + page_size < len(rows):
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"browse:page:{page+1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


async def show_browse_page(message: Message, page: int = 0):
    rows = await list_anime()
    if not rows:
        await message.answer("Hozircha katalogga anime qo‘shilmagan.")
        return
    page_size = 8
    total_pages = (len(rows) - 1) // page_size + 1
    page = max(0, min(page, total_pages - 1))
    await message.answer(
        f"📚 <b>Anime katalogi</b>\nJami: {len(rows)} ta anime\nSahifa: {page+1}/{total_pages}\n\nKo‘rish uchun animeni tanlang:",
        reply_markup=browse_keyboard(rows, page), parse_mode="HTML"
    )


@router.message(F.text == "📚 Anime katalogi")
async def open_browse_catalog(message: Message):
    if not await require_subscription(message):
        return
    await show_browse_page(message, 0)


@router.callback_query(F.data.startswith("browse:page:"))
async def browse_page_callback(call: CallbackQuery):
    if not await require_subscription(call):
        return
    try:
        page = int(call.data.rsplit(":", 1)[1])
    except ValueError:
        return await call.answer("Sahifa topilmadi", show_alert=True)
    await show_browse_page(call.message, page)
    await call.answer()


@router.callback_query(F.data.startswith("browse:anime:"))
async def browse_anime_callback(call: CallbackQuery):
    if not await require_subscription(call):
        return
    code = call.data.split(":", 2)[2]
    await show_catalog_anime(call.message, code)
    await call.answer()


@router.message(F.text == '🎟 Kod orqali topish')
async def ask_code(message: Message,state: FSMContext):
    if not await require_subscription(message): return
    await state.clear(); await state.set_state(UserState.waiting_code); await message.answer('Anime kodini yuboring:')

@router.message(UserState.waiting_code)
async def user_code_lookup(message: Message,state: FSMContext):
    if admin(message.from_user.id): return
    if not await require_subscription(message): return
    code=(message.text or '').strip().upper()
    if not await get_anime_by_code(code): return await message.answer('Bu kod bo‘yicha anime topilmadi. Kodni tekshiring:')
    await state.clear(); await show_catalog_anime(message,code)

@router.message(CommandStart(deep_link=True))
async def deep_link_start(message: Message, command, state: FSMContext):
    payload = command.args or ''
    if not payload.startswith('anime_'): return
    code=payload[6:].upper()
    if not await require_subscription(message,code): return
    await state.clear(); await show_catalog_anime(message,code)

@router.callback_query(F.data.startswith('catalog:episode:'))
async def send_episode(call: CallbackQuery):
    parts=call.data.split(':')
    code=parts[2]
    if not await require_subscription(call,code): return
    try: episode_no=int(parts[3])
    except (IndexError,ValueError): return await call.answer('Qism topilmadi',show_alert=True)
    eps=await get_episodes(code); selected=next((e for e in eps if int(e[0])==episode_no),None)
    if not selected: return await call.answer('Qism topilmadi',show_alert=True)
    no,kind,value=selected
    if kind=='telegram': await call.bot.send_video(call.from_user.id,value,caption=f'{code} — {no}-qism')
    else: await call.message.answer(f'🎬 {code} — {no}-qism\n{value}')
    await call.answer()

@router.callback_query(F.data.startswith('subscription:check'))
async def check_subscription(call: CallbackQuery):
    parts=call.data.split(':',2); code=parts[2].upper() if len(parts)>2 else None
    ok, channels = await is_subscribed(call.bot, call.from_user.id)
    if ok:
        await call.answer('✅ Obuna tasdiqlandi!',show_alert=True)
        if code: await show_catalog_anime(call.message,code)
        else: await call.message.answer('Endi 🎟 Kod orqali topish tugmasini bosing.')
    else:
        await call.answer('Hali barcha kanallarga obuna bo‘lmagansiz.',show_alert=True)
        await call.message.answer('🔒 Barcha kanallarga obuna bo‘ling:',reply_markup=required_subscription_keyboard(channels,code))
