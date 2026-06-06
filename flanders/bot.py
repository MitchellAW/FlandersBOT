import asyncio
import datetime
import logging
import os
import signal

import aiofiles
import aiohttp
import asyncpg
import discord
from discord.ext import commands

from flanders.settings.config import FlandersConfig

log = logging.getLogger(__name__)


class FlandersBOT(commands.AutoShardedBot):
    def __init__(
        self,
        config: FlandersConfig,
        session: aiohttp.ClientSession,
        db: asyncpg.Pool,
        intents: discord.Intents,
    ):
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

    async def setup_hook(self):
        # Handle sigterm from Docker
        self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.close()))

        # Initialise database
        await self.init_db()

        # Load all bot extensions from cogs folder
        for file in os.listdir("flanders/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                extension = file[:-3]

                try:
                    await self.load_extension(f"flanders.cogs.{extension}")

                except Exception as e:
                    exc = f"{type(e).__name__}: {e}"
                    log.error(f"Failed to load extension {extension}\n{exc}")

    async def db_failure(self, error_msg: str) -> None:
        log.error(f"Could not initialise the database. Closing...\n{error_msg}")
        await self.close()

    async def init_db(self):
        log.info("Initialising database...")

        async with aiofiles.open("bot.sql") as schema_file:
            schema = await schema_file.read()

        if self.db is not None:
            try:
                async with self.db.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(schema)
                log.info("Database initialised.")

            except Exception as e:
                await self.db_failure(f"{type(e).__name__}: {e}")

        else:
            await self.db_failure("DB pool was not created.")

    async def close(self):
        # Close db connection
        if self.db is not None:
            await self.db.close()

        await super().close()
