from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from app.config import get_settings
from app.db import init_db
from app.handlers import build_router
from app.web import build_web_app


logger = logging.getLogger(__name__)


async def run_bot(dispatcher: Dispatcher, bot: Bot) -> None:
    while True:
        try:
            logger.info("Starting Telegram polling")
            await dispatcher.start_polling(bot)
            return
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telegram polling crashed. Retrying in 5 seconds.")
            await asyncio.sleep(5)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = get_settings()
    init_db(settings.db_path)

    logger.info(
        "Starting web app on %s:%s with public URL %s",
        settings.web_host,
        settings.web_port,
        settings.webapp_url,
    )

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router(settings))

    web_app = build_web_app(settings)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.web_host, port=settings.web_port)
    await site.start()

    bot_task = asyncio.create_task(run_bot(dispatcher, bot))

    try:
        await bot_task
    finally:
        bot_task.cancel()
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
