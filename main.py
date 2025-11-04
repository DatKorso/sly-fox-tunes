"""Main entry point for Sly Fox Tunes bot."""

import asyncio

from aiogram import Bot, Dispatcher
from loguru import logger

from bot.handlers import download, start
from config.settings import settings


async def main() -> None:
    """Initialize and start the bot."""
    # Configure logger
    logger.add(
        "logs/bot.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    logger.info("Starting Sly Fox Tunes bot...")

    # Initialize bot and dispatcher

    # Initialize bot and dispatcher
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    # Register handlers (order matters!)
    dp.include_router(start.router)
    dp.include_router(download.router)

    logger.info("Bot handlers registered")

    try:
        # Start polling
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Graceful shutdown
        logger.info("Shutting down bot...")
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
