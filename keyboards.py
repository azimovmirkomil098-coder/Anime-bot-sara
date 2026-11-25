from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Anime qidirish"), KeyboardButton(text="🔥 Top animelar")],
            [KeyboardButton(text="❤️ Sevimlilar"), KeyboardButton(text="ℹ️ Yordam")]
        ], resize_keyboard=True
    )

def anime_results(items):
    rows = []
    for item in items[:8]:
        title = item.get("title") or "Noma’lum"
        aid = item.get("mal_id")
        rows.append([InlineKeyboardButton(text=title[:60], callback_data=f"anime:{aid}")])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

def anime_actions(anime_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Sevimlilarga qo‘shish / olib tashlash",
                              callback_data=f"fav:{anime_id}")],
        [InlineKeyboardButton(text="🔗 MyAnimeList sahifasi", url=f"https://myanimelist.net/anime/{anime_id}")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Post joylash", callback_data="admin:post")],
        [InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="admin:add_channel"),
         InlineKeyboardButton(text="➖ Kanal o‘chirish", callback_data="admin:remove_channel")],
        [InlineKeyboardButton(text="📋 Kanallar", callback_data="admin:channels"),
         InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")]
    ])

def channel_picker(channels, selected):
    rows = []
    for chat_id, title in channels:
        mark = "✅" if chat_id in selected else "▫️"
        rows.append([InlineKeyboardButton(
            text=f"{mark} {title[:45]}",
            callback_data=f"post:toggle:{chat_id}"
        )])
    rows.append([InlineKeyboardButton(text="➡️ Davom etish", callback_data="post:continue")])
    rows.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="post:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
