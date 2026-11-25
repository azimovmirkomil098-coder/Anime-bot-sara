import asyncio
import hashlib
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
from database import init_db
from handlers.users import router as users_router
from handlers.admin import router as admin_router
from handlers.posts import router as posts_router
from handlers.catalog import router as catalog_router

logging.basicConfig(level=logging.INFO)

WEBHOOK_PATH = "/telegram/webhook"
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
HOST = "0.0.0.0"
# Telegram webhook secret: only Telegram requests carrying this secret are accepted.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
if not WEBHOOK_SECRET:
    # Stable fallback so a separate secret variable is optional on Render.
    WEBHOOK_SECRET = hashlib.sha256(BOT_TOKEN.encode("utf-8")).hexdigest()


async def health(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "Anime Bot Sara"})


async def on_startup(_app: web.Application, bot: Bot) -> None:
    if not PUBLIC_URL:
        raise RuntimeError(
            "RENDER_EXTERNAL_URL topilmadi. Render Web Service muhitida avtomatik berilishi kerak."
        )
    webhook_url = f"{PUBLIC_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )
    logging.info("Webhook o‘rnatildi: %s", webhook_url)


async def main() -> None:
    await init_db()

    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(posts_router)
    dp.include_router(catalog_router)
    dp.include_router(admin_router)
    dp.include_router(users_router)

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    async def register_webhook(application: web.Application) -> None:
        await on_startup(application, bot)

    app.on_startup.append(register_webhook)

    logging.info("Anime Bot Sara Web Service sifatida ishga tushmoqda.")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    try:
        # Keep the aiohttp server alive; Render sends Telegram updates to the webhook.
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
