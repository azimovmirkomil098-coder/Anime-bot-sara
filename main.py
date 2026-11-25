import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from handlers.users import router as users_router
from handlers.admin import router as admin_router
from handlers.posts import router as posts_router


async def health_check(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info("Web health server ishga tushdi: 0.0.0.0:%s", port)

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(posts_router)
    dp.include_router(admin_router)
    dp.include_router(users_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Anime Bot Sara ishga tushdi.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
