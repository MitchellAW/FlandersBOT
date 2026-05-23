import datetime
import re
import sys
import traceback

import discord
from discord.ext import commands, tasks


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
        if self.bot.debug_mode:
            self.bot.logging = self.bot.get_channel(self.DEBUG_LOGGING_CHANNEL)

        else:
            self.bot.logging = self.bot.get_channel(self.LOGGING_CHANNEL)

    # Print bot information, update status and set uptime when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Username: {self.bot.user.name}")
        print(f"Client ID: {self.bot.user.id}")
        if not hasattr(self, "uptime"):
            self.bot.uptime = datetime.datetime.now(datetime.UTC)

    # Commands error handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Allows us to check for original exceptions raised and sent to CommandInvokeError. If nothing is found.
        # We keep the exception passed to on_command_error.
        error = getattr(error, "original", error)

        # Ignore non-existent commands
        if isinstance(error, commands.CommandNotFound):
            return

        # Check if command cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(
                f":hourglass: Sorry, command on cooldown. Please slow diddly-ding-dong down. ({time_left}s)",
                delete_after=max(error.retry_after, 5),
            )

        elif isinstance(error, commands.BotMissingPermissions):
            # List all missing permissions
            await ctx.send(
                "⛔ Sorry, I do not have the permissions riddly-required for that command-aroo!\nRequires: "
                + ", ".join(map(str, error.missing_permissions)),
                delete_after=30,
            )

        # Check for missing permissions
        elif isinstance(error, (commands.MissingPermissions, commands.errors.CheckFailure)):
            await ctx.send(
                "<:xmark:411718670482407424> Sorry, you don't have the permissions riddly-required for "
                "that command-aroo! ",
                delete_after=10,
            )

        # Check if private messages not allowed
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(f"{ctx.command} can not be used in Private Messages.")

        elif isinstance(error, Exception):
            # Get timestamp of error
            error_at = datetime.datetime.now(datetime.UTC).strftime("%y-%m-%d %H:%M:%S")

            # Print command error info and error traceback to console
            print(f"[{error_at}] Command: {ctx.command.qualified_name}", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

            # Fill paginator with error traceback
            error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
            paginator = commands.Paginator()
            error_details = f"[{error_at}] Command: {ctx.command.qualified_name}\n{error}"

            # Add error details in chunks of max paginator size
            for line in re.findall(f".{{1,{paginator.max_size - 50}}}", error_details, flags=re.S):
                paginator.add_line(line)

            # Add traceback line in chunks of max paginator size
            for line in re.findall(f".{{1, {paginator.max_size - 50}}}", str(error_traceback), flags=re.S):
                paginator.add_line(line)

            # Send error traceback to logging channel
            for page in paginator.pages:
                await self.bot.logging.send(page)

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
