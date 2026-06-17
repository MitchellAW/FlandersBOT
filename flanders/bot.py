from __future__ import annotations

import asyncio
import datetime
import logging
import signal
from typing import TYPE_CHECKING

import aiofiles
import discord
from discord.ext import commands

if TYPE_CHECKING:
    import aiohttp
    import asyncpg
    from compuglobal import Screencap

    from flanders.settings.config import FlandersConfig

log = logging.getLogger(__name__)

STARTUP_EXTENSIONS = [
    "flanders.cogs.events",
    "flanders.cogs.general",
    "flanders.cogs.owner",
    "flanders.cogs.stats",
    "flanders.cogs.trivia",
    "flanders.cogs.tv",
]


class FlandersCommandTree(discord.app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
        command = interaction.command
        if command is None:
            log.error("Ignoring exception in command tree", exc_info=error)

        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                content=f"⌛ Sorry, command on cooldown. Please slow diddly-ding-dong down. ({error.retry_after:.2f}s)",
                ephemeral=True,
            )
            log.warning("Command cooldown exceeded for %s", command.qualified_name)

        else:
            log.error("Ignoring exception in command %s", command.qualified_name, exc_info=error)


class FlandersBOT(commands.AutoShardedBot):
    def __init__(
        self,
        config: FlandersConfig,
        session: aiohttp.ClientSession,
        db: asyncpg.Pool,
        intents: discord.Intents,
    ) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            case_insensitive=True,
            intents=intents,
            tree_cls=FlandersCommandTree,
        )

        self.config = config
        self.session = session
        self.db = db

        # Remove default help command
        self.remove_command("help")

        # Default configuration with cache
        self.cached_screencaps: dict[int, tuple[Screencap, str]] = {}
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

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                content=f"⌛ Sorry, command on cooldown. Please slow diddly-ding-dong down. ({error.retry_after:.2f}s)",
                ephemeral=True,
            )
            log.warning("Command cooldown exceeded for %s", ctx.command)
        else:
            log.error("Ignoring exception in command %s", ctx.command, exc_info=error)

    async def close(self) -> None:
        # Close db connection
        if self.db is not None:
            await self.db.close()

        await super().close()
