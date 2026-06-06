import datetime
import logging

import discord
from discord.ext import commands, tasks

log = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Default status configuration
        self.status_index = 0
        self.status_formats = ["/simpsons", "/futurama"]

        # Discord channel ids used for all error logging
        self.LOGGING_CHANNEL = 797662079573557250
        self.DEBUG_LOGGING_CHANNEL = 797656963311075339

        # Start task for cycling between status formats
        self.cycle_status_format.start()

        # Load logging channel for error handling
        self.bot.loop.create_task(self.configure_logging())

    # If cog is unloaded, cancel task for cycling between status formats
    async def cog_unload(self):
        self.cycle_status_format.cancel()

    # Load logging channels for error handling
    async def configure_logging(self):
        await self.bot.wait_until_ready()
        if self.bot.config.debug_mode:
            self.bot.logging = self.bot.get_channel(self.DEBUG_LOGGING_CHANNEL)

        else:
            self.bot.logging = self.bot.get_channel(self.LOGGING_CHANNEL)

    # Log bot information, update status and set uptime when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        log.info(f"Username: {self.bot.user.name}")
        log.info(f"Client ID: {self.bot.user.id}")
        if not hasattr(self, "uptime"):
            self.bot.uptime = datetime.datetime.now(datetime.UTC)

    # Cycle through all status formats, waits 5 minutes between status changes
    # Formats status/presence with the current guild count
    @tasks.loop(minutes=5)
    async def cycle_status_format(self):
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

    # Checks if bot has permission to use external emojis in the guild, returns external emoji if permitted
    # otherwise, returns the fallback emoji
    @staticmethod
    async def use_emoji(ctx, external_emoji, fallback_emoji):
        perms = ctx.channel.permissions_for(ctx.guild.me)

        if perms.use_external_emojis:
            return external_emoji

        else:
            return fallback_emoji

    # Change the bot's status/presence to only cycle through given message
    @commands.command(hidden=True)
    @commands.is_owner()
    async def status(self, ctx, *, message: str):
        self.status_formats = [message]
        await ctx.send("Status changed! You will see an update in < 5 minutes.")

    # Add a status/presence format to the status cycle
    @commands.command(hidden=True)
    @commands.is_owner()
    async def addstatus(self, ctx, *, message: str):
        self.bot.status_formats.append(message)
        await ctx.send("Status added!")


async def setup(bot):
    await bot.add_cog(Events(bot))
