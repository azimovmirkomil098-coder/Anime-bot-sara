from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import get_channels
from keyboards import channel_picker, admin_menu

router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

class PostState(StatesGroup):
    content = State()
    choose_channels = State()
    confirm = State()

async def begin_post(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PostState.content)
    await call.message.answer(
        "📝 Kanalga yuboriladigan postni yuboring.\n"
        "Matn, rasmga caption yoki video caption yuborishingiz mumkin. "
        "Oddiy rasm/video ham qabul qilinadi."
    )

@router.message(PostState.content)
async def receive_post(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not (message.text or message.photo or message.video or message.document):
        await message.answer("Matn, rasm, video yoki hujjat yuboring.")
        return
    if message.text and len(message.text) > 4096:
        await message.answer("Matn 4096 belgidan oshmasligi kerak.")
        return
    if message.caption and len(message.caption) > 1024:
        await message.answer("Media caption 1024 belgidan oshmasligi kerak.")
        return
    data = {
        "text": message.text,
        "caption": message.caption,
        "photo": message.photo[-1].file_id if message.photo else None,
        "video": message.video.file_id if message.video else None,
        "document": message.document.file_id if message.document else None,
    }
    await state.update_data(post=data, selected=[])
    channels = await get_channels()
    if not channels:
        await state.clear()
        await message.answer("Avval admin paneldan kanal qo‘shing.", reply_markup=admin_menu())
        return
    await state.set_state(PostState.choose_channels)
    await message.answer("Post yuboriladigan kanallarni tanlang (bir nechtasini tanlash mumkin):",
                         reply_markup=channel_picker(channels, []))

@router.callback_query(PostState.choose_channels, F.data.startswith("post:toggle:"))
async def toggle_channel(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    cid = call.data.split(":", 2)[2]
    data = await state.get_data()
    selected = data.get("selected", [])
    if cid in selected:
        selected.remove(cid)
    else:
        selected.append(cid)
    await state.update_data(selected=selected)
    await call.message.edit_reply_markup(reply_markup=channel_picker(await get_channels(), selected))
    await call.answer()

@router.callback_query(PostState.choose_channels, F.data == "post:continue")
async def continue_post(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("selected"):
        await call.answer("Kamida bitta kanal tanlang.", show_alert=True)
        return
    await state.set_state(PostState.confirm)
    post = data["post"]
    await call.message.answer("👁 <b>Post ko‘rinishi:</b>", parse_mode="HTML")
    await send_content(call.message, post, preview=True)
    await call.message.answer(
        f"Tanlangan kanallar: {len(data['selected'])} ta\nPostni yuboraymi?",
        reply_markup=__import__("aiogram").types.InlineKeyboardMarkup(inline_keyboard=[
            [__import__("aiogram").types.InlineKeyboardButton(text="✅ Yuborish", callback_data="post:send"),
             __import__("aiogram").types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="post:cancel")]
        ])
    )
    await call.answer()

async def send_content(target, post, chat_id=None, preview=False):
    destination = chat_id if chat_id is not None else target.chat.id
    bot = target.bot
    text = post.get("text") or post.get("caption") or ""
    if post.get("photo"):
        await bot.send_photo(destination, post["photo"], caption=text or None)
    elif post.get("video"):
        await bot.send_video(destination, post["video"], caption=text or None)
    elif post.get("document"):
        await bot.send_document(destination, post["document"], caption=text or None)
    else:
        await bot.send_message(destination, text)

@router.callback_query(PostState.confirm, F.data == "post:send")
async def send_post(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    data = await state.get_data()
    post = data.get("post")
    selected = data.get("selected", [])
    ok, failed = [], []
    for cid in selected:
        try:
            await send_content(call.message, post, chat_id=cid)
            ok.append(cid)
        except Exception:
            failed.append(cid)
    await state.clear()
    result = f"✅ Yuborildi: {len(ok)} ta kanal."
    if failed:
        result += f"\n⚠️ Xatolik: {len(failed)} ta kanal. Bot adminligi va post huquqini tekshiring."
    await call.message.answer(result, reply_markup=admin_menu())
    await call.answer()

@router.callback_query(F.data == "post:cancel")
async def cancel_post(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    await state.clear()
    await call.message.answer("Post bekor qilindi.", reply_markup=admin_menu())
    await call.answer()
