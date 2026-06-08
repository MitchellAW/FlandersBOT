# Runs FlandersBOT
import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

import aiohttp
import asyncpg
import discord

from flanders.bot import FlandersBOT
from flanders.settings.config import FlandersConfig

log = logging.getLogger(__name__)


async def run_bot() -> None:
    # Load config from .env
    config = FlandersConfig()

    # Disable voice warnings - never used in this bot
    discord.VoiceClient.warn_dave = False
    discord.VoiceClient.warn_nacl = False

    # Setup default discord.py logging
    discord.utils.setup_logging(level=config.log_level_int)

    # Setup a rotating log file handler with similar formatting
    rotation_handler = RotatingFileHandler(
        filename=config.log_dir / "flanders.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,
    )
    rotation_handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"),
    )

    # Add rotating log file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(rotation_handler)

    # Requires members intents for leaderboard username display
    intents = discord.Intents.default()

    # Initialise bot with db pool
    try:
        db = await asyncpg.create_pool(dsn=config.postgres_dsn)
    except Exception:
        log.exception("Failed to connect to PostgreSQL. Terminating...")
        sys.exit()

    # Initialise bot with aiohttp session
    async with aiohttp.ClientSession() as session:
        bot = FlandersBOT(config=config, session=session, db=db, intents=intents)

        # Start FlandersBOT
        try:
            await bot.start(config.bot_token)

        finally:
            await bot.close()


asyncio.run(run_bot())
