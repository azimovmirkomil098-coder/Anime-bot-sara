from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_menu(is_admin=False):
    rows = [
        [KeyboardButton(text="🔎 Anime qidirish"), KeyboardButton(text="🔥 Top animelar")],
        [KeyboardButton(text="🎟 Kod orqali topish"), KeyboardButton(text="❤️ Sevimlilar")],
        [KeyboardButton(text="ℹ️ Yordam")],
    ]
    if is_admin:
        rows.append([KeyboardButton(text="🛠 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def anime_results(items):
    rows = []
    for item in items[:8]:
        title = item.get("title") or "Noma’lum"
        aid = item.get("mal_id")
        rows.append([InlineKeyboardButton(text=title[:60], callback_data=f"anime:{aid}")])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def anime_actions(anime_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❤️ Sevimlilarga qo‘shish / olib tashlash",
            callback_data=f"fav:{anime_id}",
        )],
        [InlineKeyboardButton(
            text="🔗 MyAnimeList sahifasi",
            url=f"https://myanimelist.net/anime/{anime_id}",
        )],
    ])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Anime qo‘shish", callback_data="catalog:add_anime"),
         InlineKeyboardButton(text="🎬 Qism qo‘shish", callback_data="catalog:add_episode")],
        [InlineKeyboardButton(text="📚 Anime ro‘yxati", callback_data="catalog:list")],
        [InlineKeyboardButton(text="📢 Post joylash", callback_data="admin:post")],
        [InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="admin:add_channel"),
         InlineKeyboardButton(text="➖ Kanal o‘chirish", callback_data="admin:remove_channel")],
        [InlineKeyboardButton(text="📋 Kanallar", callback_data="admin:channels"),
         InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
    ])


def channel_picker(channels, selected):
    rows = []
    for chat_id, title in channels:
        mark = "✅" if chat_id in selected else "▫️"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {title[:45]}",
            callback_data=f"post:toggle:{chat_id}",
        )])
    rows.append([InlineKeyboardButton(text="➡️ Davom etish", callback_data="post:continue")])
    rows.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="post:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def episode_picker(code, episodes):
    rows = [
        [InlineKeyboardButton(
            text=f"🎬 {episode_no}-qism",
            callback_data=f"catalog:watch:{code}:{episode_no}",
        )]
        for episode_no, _media_type, _media_value in episodes[:50]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None
