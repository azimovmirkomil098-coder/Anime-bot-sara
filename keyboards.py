from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu(is_admin=False):
    rows = [[KeyboardButton(text="📚 Anime katalogi"), KeyboardButton(text="🔎 Anime qidirish")],
            [KeyboardButton(text="🔥 Top animelar"), KeyboardButton(text="❤️ Sevimlilar")],
            [KeyboardButton(text="🎟 Kod orqali topish"), KeyboardButton(text="ℹ️ Yordam")]]
    if is_admin:
        rows.append([KeyboardButton(text="🛠 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def anime_results(items):
    rows = []
    for item in items[:8]:
        anime_id = item.get("mal_id")
        if anime_id is None:
            continue
        title = (item.get("title") or "Noma’lum").replace("\n", " ")
        rows.append([InlineKeyboardButton(text=title[:60], callback_data=f"anime:{anime_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def anime_actions(anime_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Sevimlilarga qo‘shish / olib tashlash", callback_data=f"fav:{anime_id}")],
        [InlineKeyboardButton(text="🔗 MyAnimeList sahifasi", url=f"https://myanimelist.net/anime/{anime_id}")]])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Anime qo‘shish", callback_data="catalog:add_anime"),
         InlineKeyboardButton(text="🎬 Qism qo‘shish", callback_data="catalog:add_episode")],
        [InlineKeyboardButton(text="���� Anime ro‘yxati", callback_data="catalog:list")],
        [InlineKeyboardButton(text="📢 Post joylash", callback_data="admin:post")],
        [InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="admin:add_channel"),
         InlineKeyboardButton(text="➖ Kanal o‘chirish", callback_data="admin:remove_channel")],
        [InlineKeyboardButton(text="📋 Kanallar", callback_data="admin:channels"),
         InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🔒 Majburiy obuna sozlamalari", callback_data="admin:sub_channels")]])


def channel_picker(channels, selected):
    rows = []
    for chat_id, title in channels:
        marker = "✅" if str(chat_id) in selected else "▫️"
        rows.append([InlineKeyboardButton(text=f"{marker} {title[:45]}", callback_data=f"post:toggle:{chat_id}")])
    rows += [[InlineKeyboardButton(text="➡️ Davom etish", callback_data="post:continue")],
             [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="post:cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def required_subscription_keyboard(channels, anime_code=None):
    rows = [[InlineKeyboardButton(text=f"➕ {title[:45]}", url=link)]
            for _chat_id, title, link in channels if link]
    check_data = f"subscription:check:{anime_code}" if anime_code else "subscription:check"
    rows.append([InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data=check_data)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def anime_episode_keyboard(code, episodes):
    rows = [[InlineKeyboardButton(text=f"▶️ {number}-qism", callback_data=f"catalog:episode:{code}:{number}")]
            for number, _kind, _value in episodes]
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None
