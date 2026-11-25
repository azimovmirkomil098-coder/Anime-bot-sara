import aiosqlite
from config import DATABASE_PATH

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS channels (chat_id TEXT PRIMARY KEY, title TEXT NOT NULL)')
        await db.execute('CREATE TABLE IF NOT EXISTS required_channels (chat_id TEXT PRIMARY KEY, title TEXT NOT NULL, invite_link TEXT NOT NULL)')
        await db.execute('CREATE TABLE IF NOT EXISTS favorites (user_id INTEGER NOT NULL, anime_id INTEGER NOT NULL, title TEXT NOT NULL, PRIMARY KEY(user_id, anime_id))')
        await db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        await db.execute('''CREATE TABLE IF NOT EXISTS anime_catalog (
            code TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT DEFAULT '', poster_file_id TEXT,
            genre TEXT DEFAULT '', release_year TEXT DEFAULT '', language TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS anime_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, anime_code TEXT NOT NULL, episode_no INTEGER NOT NULL,
            media_type TEXT NOT NULL, media_value TEXT NOT NULL,
            UNIQUE(anime_code, episode_no), FOREIGN KEY(anime_code) REFERENCES anime_catalog(code))''')
        # Mavjud bazalarga yangi ustunlarni xavfsiz qo‘shish
        cur = await db.execute('PRAGMA table_info(anime_catalog)')
        columns = {row[1] for row in await cur.fetchall()}
        for name in ('genre', 'release_year', 'language'):
            if name not in columns:
                await db.execute(f"ALTER TABLE anime_catalog ADD COLUMN {name} TEXT DEFAULT ''")
        await db.commit()

async def add_user(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('INSERT OR IGNORE INTO users(user_id) VALUES(?)', (user_id,)); await db.commit()
async def add_channel(chat_id, title):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO channels(chat_id,title) VALUES(?,?)', (str(chat_id),title)); await db.commit()
async def remove_channel(chat_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('DELETE FROM channels WHERE chat_id=?',(str(chat_id),)); await db.commit()
async def get_channels():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT chat_id,title FROM channels ORDER BY title')).fetchall()
async def toggle_favorite(user_id, anime_id, title):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur=await db.execute('SELECT 1 FROM favorites WHERE user_id=? AND anime_id=?',(user_id,anime_id)); exists=await cur.fetchone()
        if exists:
            await db.execute('DELETE FROM favorites WHERE user_id=? AND anime_id=?',(user_id,anime_id)); result=False
        else:
            await db.execute('INSERT INTO favorites(user_id,anime_id,title) VALUES(?,?,?)',(user_id,anime_id,title)); result=True
        await db.commit(); return result
async def get_favorites(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT anime_id,title FROM favorites WHERE user_id=? ORDER BY title',(user_id,))).fetchall()
async def get_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        users=await (await db.execute('SELECT COUNT(*) FROM users')).fetchone(); channels=await (await db.execute('SELECT COUNT(*) FROM channels')).fetchone(); anime=await (await db.execute('SELECT COUNT(*) FROM anime_catalog')).fetchone()
        return users[0],channels[0],anime[0]
async def create_anime(code,title,description='',poster_file_id=None,genre='',release_year='',language=''):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('INSERT INTO anime_catalog(code,title,description,poster_file_id,genre,release_year,language) VALUES(?,?,?,?,?,?,?)',(code.upper(),title,description,poster_file_id,genre,release_year,language)); await db.commit()
async def get_anime_by_code(code):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT code,title,description,poster_file_id,genre,release_year,language FROM anime_catalog WHERE code=?',(code.upper(),))).fetchone()
async def list_anime():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT code,title FROM anime_catalog ORDER BY title')).fetchall()
async def add_episode(code,episode_no,media_type,media_value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO anime_episodes(anime_code,episode_no,media_type,media_value) VALUES(?,?,?,?)',(code.upper(),int(episode_no),media_type,media_value)); await db.commit()
async def get_episodes(code):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT episode_no,media_type,media_value FROM anime_episodes WHERE anime_code=? ORDER BY CAST(episode_no AS INTEGER)',(code.upper(),))).fetchall()
async def add_required_channel(chat_id, title, invite_link):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO required_channels(chat_id,title,invite_link) VALUES(?,?,?)', (str(chat_id), title, invite_link)); await db.commit()
async def remove_required_channel(chat_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('DELETE FROM required_channels WHERE chat_id=?', (str(chat_id),)); await db.commit()
async def get_required_channels():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        return await (await db.execute('SELECT chat_id,title,invite_link FROM required_channels ORDER BY title')).fetchall()
