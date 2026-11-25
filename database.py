import aiosqlite
from config import DATABASE_PATH

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS channels (
            chat_id TEXT PRIMARY KEY,
            title TEXT NOT NULL
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            anime_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            PRIMARY KEY(user_id, anime_id)
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        await db.commit()

async def add_user(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
        await db.commit()

async def add_channel(chat_id: str, title: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO channels(chat_id,title) VALUES(?,?)", (chat_id, title))
        await db.commit()

async def remove_channel(chat_id: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM channels WHERE chat_id=?", (chat_id,))
        await db.commit()

async def get_channels():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT chat_id,title FROM channels ORDER BY title")
        return await cur.fetchall()

async def toggle_favorite(user_id: int, anime_id: int, title: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "SELECT 1 FROM favorites WHERE user_id=? AND anime_id=?",
            (user_id, anime_id)
        )
        exists = await cur.fetchone()
        if exists:
            await db.execute("DELETE FROM favorites WHERE user_id=? AND anime_id=?", (user_id, anime_id))
            result = False
        else:
            await db.execute("INSERT INTO favorites(user_id,anime_id,title) VALUES(?,?,?)",
                             (user_id, anime_id, title))
            result = True
        await db.commit()
        return result

async def get_favorites(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT anime_id,title FROM favorites WHERE user_id=? ORDER BY title", (user_id,))
        return await cur.fetchall()

async def get_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        channels = await (await db.execute("SELECT COUNT(*) FROM channels")).fetchone()
        return users[0], channels[0]
