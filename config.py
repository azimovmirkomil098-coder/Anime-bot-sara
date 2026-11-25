import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip().isdigit()
}
DATABASE_PATH = os.getenv("DATABASE_PATH", "anime_bot.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida kiritilmagan.")
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS .env faylida kamida bitta admin ID bo‘lishi kerak.")
