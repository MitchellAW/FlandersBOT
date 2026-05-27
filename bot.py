import asyncio
import datetime
import os
import signal
import sys

import aiofiles
import aiohttp
import asyncpg
import discord
from discord.ext import commands

from settings.config import FlandersConfig


class FlandersBOT(commands.AutoShardedBot):
    def __init__(self, config: FlandersConfig, intents: discord.Intents):
        super().__init__(command_prefix=self.get_default_prefixes, case_insensitive=True, intents=intents)

        self.config = config

        # Remove default help command
        self.remove_command("help")

        # Default configuration with cache
        self.cached_screencaps = {}
        self.reminders = []
        self.uptime = datetime.datetime.now(datetime.UTC)
        self.db: asyncpg.Pool | None = None
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self):
        # Handle sigterm from Docker
        self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.close()))

        # Initialise database
        await self.init_db()

        # Load all bot extensions from cogs folder
        for file in os.listdir("cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                extension = file[:-3]

                try:
                    await self.load_extension(f"cogs.{extension}")

                except Exception as e:
                    exc = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exc}")

    async def db_failure(self, error_msg: str) -> None:
        print(f"Could not initialise the database. Closing...\n{error_msg}")
        await self.close()

    async def init_db(self):
        print("Initialising database...")

        async with aiofiles.open("bot.sql") as schema_file:
            schema = await schema_file.read()

        if self.db is not None:
            try:
                async with self.db.acquire() as conn:
                    async with conn.transaction():
                        await conn.execute(schema)
                print("Database initialised.")

            except Exception as e:
                await self.db_failure(f"{type(e).__name__}: {e}")

        else:
            await self.db_failure("DB pool was not created.")

    async def close(self):
        # Close db connection
        if self.db is not None:
            await self.db.close()

        await super().close()

    # Default get prefixes method, only supports mentions without message content privileges
    async def get_default_prefixes(self, bot, message):
        return commands.when_mentioned(self, message)


# Runs FlandersBOT
async def run_bot():
    # Requires members intents for leaderboard username display
    intents = discord.Intents.default()

    # Load config from .env
    config = FlandersConfig()

    # Configure bot with config/intents
    bot = FlandersBOT(config=config, intents=intents)

    # Initialise bot with db pool
    try:
        bot.db = await asyncpg.create_pool(dsn=config.postgres_dsn)
    except Exception as e:
        print(f"Failed to connect PostgreSQL. Terminating.\n{type(e).__name__}: {e}")
        sys.exit()

    # Initialise bot with aiohttp session
    async with aiohttp.ClientSession() as session:
        bot.session = session

        # Start FlandersBOT
        try:
            await bot.start(config.bot_token)

        finally:
            await bot.close()


asyncio.run(run_bot())
