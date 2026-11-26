from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import add_channel, remove_channel, get_channels, get_stats, add_required_channel, remove_required_channel, get_required_channels
from keyboards import admin_menu

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminState(StatesGroup):
    add_channel = State()
    remove_channel = State()
    add_sub_channel = State()
    remove_sub_channel = State()


@router.message(F.text == "/admin")
async def admin_start(message: Message):
    if is_admin(message.from_user.id):
        await message.answer("🛠 <b>Admin panel</b>", reply_markup=admin_menu(), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin:"))
async def admin_actions(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo‘q.", show_alert=True)
        return
    action = call.data.split(":")[1]
    if action == "add_channel":
        await state.set_state(AdminState.add_channel)
        await call.message.answer("Kanal username yoki ID sini yuboring. Masalan: @anime_kanal yoki -1001234567890")
    elif action == "remove_channel":
        channels = await get_channels()
        if not channels:
            await call.message.answer("Saqlangan kanal yo‘q.")
        else:
            await state.set_state(AdminState.remove_channel)
            await call.message.answer("O‘chirmoqchi bo‘lgan kanal ID sini yuboring:\n" + "\n".join(f"{title}: {cid}" for cid, title in channels))
    elif action == "channels":
        channels = await get_channels()
        await call.message.answer("📋 Kanallar:\n" + ("\n".join(f"• {title} — {cid}" for cid, title in channels) or "Hozircha kanal yo‘q."))
    elif action == "stats":
        users, channels, anime = await get_stats()
        await call.message.answer(f"📊 Foydalanuvchilar: {users}\n📢 Kanallar: {channels}\n🎌 Animelar: {anime}")
    elif action == "sub_channels":
        channels = await get_required_channels()
        listing = "\n".join(f"• {title} — {cid}" for cid, title, _link in channels) or "Hozircha majburiy obuna kanali yo‘q."
        await call.message.answer("🔒 <b>Majburiy obuna kanallari</b>\n" + listing + "\n\nKanal qo‘shish uchun quyidagi tugmalardan foydalaning.",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="admin:sub_add")],
                                     [InlineKeyboardButton(text="➖ Kanal o‘chirish", callback_data="admin:sub_remove")]]),
                                 parse_mode="HTML")
    elif action == "sub_add":
        await state.set_state(AdminState.add_sub_channel)
        await call.message.answer("Majburiy obuna qilinadigan kanal username yoki ID sini yuboring (masalan @kanal yoki -100... ). Bot kanalda admin bo‘lishi shart.")
    elif action == "sub_remove":
        channels = await get_required_channels()
        if not channels:
            await call.message.answer("Majburiy obuna kanallari ro‘yxati bo‘sh.")
        else:
            await state.set_state(AdminState.remove_sub_channel)
            await call.message.answer("O‘chirmoqchi bo‘lgan kanal ID sini yuboring:\n" + "\n".join(f"{title}: {cid}" for cid, title, _link in channels))
    elif action == "post":
        from handlers.posts import begin_post
        await begin_post(call, state)
    await call.answer()


@router.message(AdminState.add_channel)
async def save_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    value = (message.text or "").strip()
    try:
        chat = await message.bot.get_chat(value)
        member = await message.bot.get_chat_member(chat.id, message.bot.id)
        if member.status not in ("administrator", "creator"):
            await message.answer("Bot bu kanalda admin emas. Avval botni kanalga admin qiling.")
            return
        await add_channel(str(chat.id), chat.title or value)
        await state.clear()
        await message.answer(f"✅ Kanal qo‘shildi: {chat.title}", reply_markup=admin_menu())
    except Exception:
        await message.answer("Kanal topilmadi yoki bot kanalga qo‘shilmagan. @username yoki -100... ID ni tekshiring.")


@router.message(AdminState.remove_channel)
async def delete_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await remove_channel((message.text or "").strip())
    await state.clear()
    await message.answer("Kanal ro‘yxatdan o‘chirildi.", reply_markup=admin_menu())


@router.message(AdminState.add_sub_channel)
async def save_required_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    value = (message.text or "").strip()
    try:
        chat = await message.bot.get_chat(value)
        member = await message.bot.get_chat_member(chat.id, message.bot.id)
        if member.status not in ("administrator", "creator"):
            await message.answer("Bot bu kanalda admin emas. Avval botni kanalga admin qiling.")
            return
        link = f"https://t.me/{chat.username}" if chat.username else await message.bot.export_chat_invite_link(chat.id)
        await add_required_channel(chat.id, chat.title or value, link)
        await state.clear()
        await message.answer(f"✅ Majburiy obuna kanali qo‘shildi: {chat.title}", reply_markup=admin_menu())
    except Exception:
        await message.answer("Kanal topilmadi yoki botda admin huquqi yo‘q. Kanal username/ID sini tekshiring.")


@router.message(AdminState.remove_sub_channel)
async def delete_required_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await remove_required_channel((message.text or "").strip())
    await state.clear()
    await message.answer("✅ Majburiy obuna kanali o‘chirildi.", reply_markup=admin_menu())
