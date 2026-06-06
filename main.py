# Runs FlandersBOT
import asyncio
import logging
import sys

import aiohttp
import asyncpg
import discord

from flanders.bot import FlandersBOT
from flanders.settings.config import FlandersConfig

# Use default logging configuration
discord.utils.setup_logging()
log = logging.getLogger(__name__)


async def run_bot():

    # Requires members intents for leaderboard username display
    intents = discord.Intents.default()

    # Load config from .env
    config = FlandersConfig()

    # Initialise bot with db pool
    try:
        db = await asyncpg.create_pool(dsn=config.postgres_dsn)
    except Exception as e:
        log.error(f"Failed to connect PostgreSQL. Terminating.\n{type(e).__name__}: {e}")
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
