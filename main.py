# Runs FlandersBOT
import asyncio
import logging
import sys

import aiohttp
import asyncpg
import discord

from flanders.bot import FlandersBOT
from flanders.settings.config import FlandersConfig
from flanders.utils import setup_logging

log = logging.getLogger(__name__)

async def run_bot() -> None:
    # Load config from .env
    config = FlandersConfig()

    # Disable voice warnings - never used in this bot
    discord.VoiceClient.warn_dave = False
    discord.VoiceClient.warn_nacl = False

    # Setup default discord.py logging
    discord.utils.setup_logging(level=config.log_level_int)

    # Setup logging with given config
    setup_logging(config)

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
