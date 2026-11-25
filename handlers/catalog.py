from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import create_anime, get_anime_by_code, list_anime, add_episode, get_episodes

router = Router()

def admin(uid): return uid in ADMIN_IDS

class UserState(StatesGroup):
    waiting_code = State()

class CatalogState(StatesGroup):
    anime_title = State(); anime_code = State(); anime_description = State(); anime_poster = State()
    episode_code = State(); episode_number = State(); episode_media = State()

@router.callback_query(F.data == 'catalog:add_anime')
async def add_anime_start(call: CallbackQuery, state: FSMContext):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q', show_alert=True)
    await state.clear(); await state.set_state(CatalogState.anime_title)
    await call.message.answer('Anime nomini yuboring:')
    await call.answer()

@router.message(CatalogState.anime_title)
async def anime_title(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    title=(message.text or '').strip()
    if len(title)<2: return await message.answer('Nom kamida 2 ta belgidan iborat bo‘lsin.')
    await state.update_data(title=title); await state.set_state(CatalogState.anime_code)
    await message.answer('Anime uchun takrorlanmaydigan kod kiriting (masalan: A101):')

@router.message(CatalogState.anime_code)
async def anime_code(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    code=(message.text or '').strip().upper()
    if not code or len(code)>20 or not code.replace('_','').replace('-','').isalnum():
        return await message.answer('Kod faqat harf, raqam, _ yoki - dan iborat bo‘lsin.')
    if await get_anime_by_code(code): return await message.answer('Bu kod band. Boshqa kod kiriting:')
    await state.update_data(code=code); await state.set_state(CatalogState.anime_description)
    await message.answer('Anime tavsifini yuboring. Kerak bo‘lmasa /skip yozing:')

@router.message(CatalogState.anime_description)
async def anime_description(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    desc='' if message.text=='/skip' else (message.text or '').strip()
    await state.update_data(description=desc); await state.set_state(CatalogState.anime_poster)
    await message.answer('Anime posterini rasm qilib yuboring yoki /skip yozing:')

@router.message(CatalogState.anime_poster)
async def anime_poster(message: Message, state: FSMContext):
    if not admin(message.from_user.id): return
    if message.text != '/skip' and not message.photo:
        return await message.answer('Rasm yuboring yoki postersiz davom etish uchun /skip yozing.')
    data=await state.get_data(); poster=message.photo[-1].file_id if message.photo else None
    try:
        await create_anime(data['code'],data['title'],data['description'],poster)
    except Exception:
        await message.answer('Anime saqlanmadi. Kod band bo‘lishi mumkin. /admin orqali qayta urinib ko‘ring.')
        await state.clear(); return
    await state.clear()
    await message.answer(f"✅ Anime qo‘shildi!\n🎌 {data['title']}\n🔑 Kod: <code>{data['code']}</code>",parse_mode='HTML')

@router.callback_query(F.data == 'catalog:add_episode')
async def add_episode_start(call: CallbackQuery,state: FSMContext):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    await state.clear(); await state.set_state(CatalogState.episode_code)
    await call.message.answer('Qism qo‘shiladigan anime kodini yuboring:')
    await call.answer()

@router.message(CatalogState.episode_code)
async def episode_code(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    code=(message.text or '').strip().upper(); anime=await get_anime_by_code(code)
    if not anime: return await message.answer('Bunday kodli anime topilmadi. To‘g‘ri kod kiriting:')
    await state.update_data(code=code,title=anime[1]); await state.set_state(CatalogState.episode_number)
    await message.answer(f"{anime[1]} uchun qism raqamini yuboring (masalan: 1 yoki 1-qism):")

@router.message(CatalogState.episode_number)
async def episode_number(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    no=(message.text or '').strip()
    if not no or len(no)>20: return await message.answer('Qism raqamini to‘g‘ri kiriting:')
    await state.update_data(episode_no=no); await state.set_state(CatalogState.episode_media)
    await message.answer('Endi videoni Telegram orqali yuboring yoki video URL havolasini yuboring:')

@router.message(CatalogState.episode_media)
async def episode_media(message: Message,state: FSMContext):
    if not admin(message.from_user.id): return
    if message.video:
        kind='telegram'; value=message.video.file_id
    else:
        value=(message.text or '').strip()
        if not (value.startswith('https://') or value.startswith('http://')):
            return await message.answer('Video yuboring yoki http:// / https:// bilan boshlanuvchi URL kiriting.')
        kind='url'
    data=await state.get_data()
    try: await add_episode(data['code'],data['episode_no'],kind,value)
    except Exception: return await message.answer('Qismni saqlashda xatolik. Qayta yuboring.')
    await state.clear()
    await message.answer(f"✅ {data['title']} — {data['episode_no']} saqlandi.")

@router.callback_query(F.data == 'catalog:list')
async def catalog_list(call: CallbackQuery):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    rows=await list_anime()
    if not rows: await call.message.answer('Hozircha anime qo‘shilmagan.')
    else:
        for code,title in rows[:50]:
            eps=await get_episodes(code)
            await call.message.answer(f'🎌 <b>{title}</b>\n🔑 Kod: <code>{code}</code>\n🎬 Qismlar: {len(eps)}',parse_mode='HTML',reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📢 Kanalga post qilish',callback_data=f'catalog:post:{code}')]]))
    await call.answer()

@router.callback_query(F.data.startswith('catalog:post:'))
async def post_anime_info(call: CallbackQuery):
    if not admin(call.from_user.id): return await call.answer('Ruxsat yo‘q',show_alert=True)
    code=call.data.split(':',2)[2]; anime=await get_anime_by_code(code)
    if not anime: return await call.answer('Anime topilmadi',show_alert=True)
    from database import get_channels
    channels=await get_channels()
    if not channels: return await call.answer('Avval kanal qo‘shing',show_alert=True)
    text=f'🎌 <b>{anime[1]}</b>\n🔑 Kod: <code>{anime[0]}</code>\n\n{anime[2] or "Tavsif mavjud emas."}'
    sent=0
    for cid,_ in channels:
        try:
            if anime[3]: await call.bot.send_photo(cid,anime[3],caption=text,parse_mode='HTML')
            else: await call.bot.send_message(cid,text,parse_mode='HTML')
            sent+=1
        except Exception: pass
    await call.message.answer(f'📢 Anime {sent}/{len(channels)} ta kanalga joylandi.')
    await call.answer()

@router.message(F.text == '🎟 Kod orqali topish')
async def ask_code(message: Message,state: FSMContext):
    await state.clear(); await state.set_state(UserState.waiting_code)
    await message.answer('Anime kodini yuboring:')

@router.message(UserState.waiting_code)
async def user_code_lookup(message: Message,state: FSMContext):
    if admin(message.from_user.id): return
    code=(message.text or '').strip().upper(); anime=await get_anime_by_code(code)
    if not anime: return await message.answer('Bu kod bo‘yicha anime topilmadi. Kodni tekshiring:')
    eps=await get_episodes(code)
    caption=f'🎌 <b>{anime[1]}</b>\n🔑 Kod: <code>{code}</code>\n\n{anime[2] or "Tavsif mavjud emas."}'
    if anime[3]: await message.answer_photo(anime[3],caption=caption,parse_mode='HTML')
    else: await message.answer(caption,parse_mode='HTML')
    if not eps: await message.answer('Hozircha qismlar qo‘shilmagan.')
    else:
        kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f'▶️ {no}',callback_data=f'catalog:episode:{code}:{i}')] for i,(no,_,_) in enumerate(eps)])
        await message.answer('Qismni tanlang:',reply_markup=kb)
    await state.clear()

@router.callback_query(F.data.startswith('catalog:episode:'))
async def send_episode(call: CallbackQuery):
    parts=call.data.split(':'); code=parts[2]; index=int(parts[3]); eps=await get_episodes(code)
    if index>=len(eps): return await call.answer('Qism topilmadi',show_alert=True)
    no,kind,value=eps[index]
    if kind=='telegram': await call.bot.send_video(call.from_user.id,value,caption=f'{code} — {no}')
    else: await call.message.answer(f'🎬 {code} — {no}\n{value}')
    await call.answer()
