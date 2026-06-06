import asyncio
import datetime
import logging
import signal

import aiofiles
import aiohttp
import asyncpg
import discord
from discord.ext import commands

from flanders.settings.config import FlandersConfig

log = logging.getLogger(__name__)

STARTUP_EXTENSIONS = [
    "flanders.cogs.events",
    "flanders.cogs.futurama",
    "flanders.cogs.general",
    "flanders.cogs.owner",
    "flanders.cogs.rickandmorty",
    "flanders.cogs.simpsons",
    "flanders.cogs.stats",
    "flanders.cogs.trivia",
]


class FlandersBOT(commands.AutoShardedBot):
    def __init__(
        self,
        config: FlandersConfig,
        session: aiohttp.ClientSession,
        db: asyncpg.Pool,
        intents: discord.Intents,
    ) -> None:
        super().__init__(command_prefix=commands.when_mentioned, case_insensitive=True, intents=intents)

        self.config = config
        self.session = session
        self.db = db

        # Remove default help command
        self.remove_command("help")

        # Default configuration with cache
        self.cached_screencaps = {}
        self.reminders = []
        self.uptime = datetime.datetime.now(datetime.UTC)

    async def setup_hook(self) -> None:
        # Handle sigterm from Docker
        self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.close()))

        # Initialise database
        await self.init_db()

        # Load all bot extensions from cogs folder
        for extension in STARTUP_EXTENSIONS:
            try:
                await self.load_extension(extension)

            except Exception:
                log.exception("Failed to load extension")

    async def init_db(self) -> None:
        log.info("Initialising database...")

        async with aiofiles.open("bot.sql") as schema_file:
            schema = await schema_file.read()

        if self.db is not None:
            try:
                async with self.db.acquire() as conn, conn.transaction():
                    await conn.execute(schema)
                log.info("Database initialised.")

            except Exception:
                log.exception("Failed to acquire database")

        else:
            log.error("DB pool was not created")

    async def close(self) -> None:
        # Close db connection
        if self.db is not None:
            await self.db.close()

        await super().close()
