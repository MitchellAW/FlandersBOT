import datetime
import logging

import discord
from discord.ext import commands, tasks

from flanders.bot import FlandersBOT

log = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot: FlandersBOT) -> None:
        self.bot = bot

        # Default status configuration
        self.status_index = 0
        self.status_formats = ["/simpsons", "/futurama"]

        # Discord channel ids used for all error logging
        self.LOGGING_CHANNEL = 797662079573557250
        self.DEBUG_LOGGING_CHANNEL = 797656963311075339

        # Start task for cycling between status formats
        self.cycle_status_format.start()

    # If cog is unloaded, cancel task for cycling between status formats
    async def cog_unload(self) -> None:
        self.cycle_status_format.cancel()

    # Log bot information, update status and set uptime when bot is ready
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if self.bot.user is not None:
            log.info("Username: %s", self.bot.user.name)
            log.info("Client ID: %s", str(self.bot.user.id))

        else:
            log.error("Bot User does not exist")
        if not hasattr(self, "uptime"):
            self.bot.uptime = datetime.datetime.now(datetime.UTC)

    # Cycle through all status formats, waits 5 minutes between status changes
    # Formats status/presence with the current guild count
    @tasks.loop(minutes=5)
    async def cycle_status_format(self) -> None:
        await self.bot.wait_until_ready()
        if self.status_index >= len(self.status_formats) - 1:
            self.status_index = 0

        # Update presence/status
        status = self.status_formats[self.status_index]
        if "{}" in status:
            status = status.format(len(self.bot.guilds))

        # Display status as 'Try /simpsons' etc.
        status = f"Try {status}"
        activity = discord.CustomActivity(name=status)
        await self.bot.change_presence(activity=activity)

        # Only increment status index after a status change
        self.status_index += 1


async def setup(bot: FlandersBOT) -> None:
    await bot.add_cog(Events(bot))
