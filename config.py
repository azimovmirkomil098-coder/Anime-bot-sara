import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = set()
for _value in _admin_ids_raw.split(","):
    _value = _value.strip()
    if _value:
        try:
            _admin_id = int(_value)
        except ValueError as exc:
            raise RuntimeError(f"ADMIN_IDS ichida noto‘g‘ri qiymat: {_value!r}") from exc
        if _admin_id <= 0:
            raise RuntimeError("ADMIN_IDS dagi Telegram user ID musbat son bo‘lishi kerak.")
        ADMIN_IDS.add(_admin_id)

DATABASE_PATH = os.getenv("DATABASE_PATH", "anime_bot.db").strip() or "anime_bot.db"
# Expand a leading ~ while keeping relative paths relative to the process working directory.
DATABASE_PATH = str(Path(DATABASE_PATH).expanduser())

if not BOT_TOKEN or BOT_TOKEN == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
    raise RuntimeError("BOT_TOKEN .env faylida kiritilmagan.")
if not ADMIN_IDS:
    raise RuntimeError("ADMIN_IDS .env faylida kamida bitta admin ID bo‘lishi kerak.")
