import asyncio
import hashlib
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
from database import init_db
from handlers.admin import router as admin_router
from handlers.catalog import router as catalog_router
from handlers.posts import router as posts_router
from handlers.users import router as users_router

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
WEBHOOK_PATH = "/telegram/webhook"
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
HOST = "0.0.0.0"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
if not WEBHOOK_SECRET:
    WEBHOOK_SECRET = hashlib.sha256(BOT_TOKEN.encode("utf-8")).hexdigest()


class NavigationResetMiddleware(BaseMiddleware):
    MENU_TEXTS = {"📚 Anime katalogi", "🔎 Anime qidirish", "🔥 Top animelar", "❤️ Sevimlilar",
                  "🎟 Kod orqali topish", "ℹ️ Yordam", "🛠 Admin panel", "/start", "/admin", "/cancel"}

    async def __call__(self, handler, event, data):
        state = data.get("state")
        if state is not None:
            if isinstance(event, Message):
                text = (event.text or "").strip()
                if text in self.MENU_TEXTS or text.startswith("/start "):
                    await state.clear()
            elif isinstance(event, CallbackQuery):
                callback_data = event.data or ""
                if callback_data.startswith(("admin:", "catalog:", "browse:", "anime:", "fav:")):
                    await state.clear()
        return await handler(event, data)


async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "Anime Bot Sara"})


async def on_startup(bot: Bot) -> None:
    if not PUBLIC_URL:
        raise RuntimeError("RENDER_EXTERNAL_URL topilmadi. Render Web Service muhitida avtomatik berilishi kerak.")
    await bot.set_webhook(url=f"{PUBLIC_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET,
                          allowed_updates=["message", "callback_query"], drop_pending_updates=True)
    logging.info("Webhook o‘rnatildi: %s%s", PUBLIC_URL, WEBHOOK_PATH)


async def main() -> None:
    await init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    navigation_reset = NavigationResetMiddleware()
    dp.message.outer_middleware(navigation_reset)
    dp.callback_query.outer_middleware(navigation_reset)
    dp.include_router(posts_router)
    dp.include_router(catalog_router)
    dp.include_router(admin_router)
    dp.include_router(users_router)

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def register_webhook(_application: web.Application) -> None:
        await on_startup(bot)

    app.on_startup.append(register_webhook)
    logging.info("Anime Bot Sara Web Service sifatida ishga tushmoqda.")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
