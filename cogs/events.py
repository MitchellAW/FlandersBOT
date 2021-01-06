import json
import sys
import traceback
from datetime import datetime

import aiohttp
import asyncio
import asyncpg
import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Default status configuration
        self.status_index = 0
        self.status_formats = ['Ned help | {} Servers', 'Ned vote | {} Servers']

        # Initialise command stats
        self.bot.command_stats = self.read_command_stats()

        # Create background tasks for cycling status format
        self.bot.bg_task = self.bot.loop.create_task(self.cycle_status_format())

    # Print bot information, update status and set uptime when bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Username: {self.bot.user.name}')
        print(f'Client ID: {self.bot.user.id}')
        await self.update_status()
        if not hasattr(self, 'uptime'):
            self.bot.uptime = datetime.utcnow()

    # Update guild count on join
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_status()

    # Update guild count on leave
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.update_status()

    # Track number of command executed
    @commands.Cog.listener()
    async def on_command(self, ctx):
        command = ctx.command.qualified_name
        if command in self.bot.command_stats:
            self.bot.command_stats[command] += 1

        else:
            self.bot.command_stats[command] = 1

        self.write_command_stats(self.bot.command_stats)

    # Commands error handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Allows us to check for original exceptions raised and sent to CommandInvokeError. If nothing is found.
        # We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Channel in FlandersBOT server for logging errors to
        logging = self.bot.get_channel(self.bot.LOGGING_CHANNEL)

        # Ignore non-existent commands
        if isinstance(error, commands.CommandNotFound):
            return

        # Check if command cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(f':hourglass: Command on cooldown. Slow diddly-ding-dong down. ({time_left}s)',
                           delete_after=max(error.retry_after, 5))

        elif isinstance(error, commands.BotMissingPermissions):

            # List all missing permissions
            await ctx.send('⛔ Sorry, I do not have the permissions riddly-required for that command-aroo!\nRequires: ' +
                           ', '.join(map(str, error.missing_perms)))

        # Check for missing permissions
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('<:xmark:411718670482407424> Sorry, you don\'t have the permissions riddly-required for '
                           'that command-aroo! ')

        # Check if private messages not allowed
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        else:
            await logging.send(f'Command: {ctx.command.qualified_name}')
            await logging.send(error)

            # Send error traceback to logging channel
            error_traceback = traceback.format_exception(type(error), error, error.__traceback__)
            paginator = commands.Paginator()
            for line in error_traceback:
                paginator.add_line(line)

            for page in paginator.pages:
                await logging.send(page)

            # Print error traceback to console
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # Update guild count at bot listing sites and in bots status/presence
    async def update_status(self):
        await self.update_guild_counts()
        status = discord.Game(name=self.status_formats[self.status_index].format(str(len(self.bot.guilds))))
        await self.bot.change_presence(activity=status)

    # Cycle through all status formats, waits a minute between status changes
    async def cycle_status_format(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.status_index >= len(self.status_formats) - 1:
                self.status_index = 0

            else:
                self.status_index += 1

            status = discord.Game(name=self.status_formats[self.status_index].format(str(len(self.bot.guilds))))

            await self.bot.change_presence(activity=status)
            await asyncio.sleep(60)

    # Post guild count to update count for bot_listing sites
    async def update_guild_counts(self):
        for listing in self.bot.config['bot_listings']:
            async with aiohttp.ClientSession() as session:
                url = listing['url'].format(str(self.bot.user.id))
                data = {
                    listing['payload']['guild_count']: len(self.bot.guilds)
                }
                headers = listing['headers']

                # Check if api needs payload posted as data or json
                if listing['posts_data']:
                    await session.post(url, data=data, headers=headers, timeout=15)

                else:
                    await session.post(url, json=data, headers=headers, timeout=15)

    # Read the command statistics from json file
    @staticmethod
    def read_command_stats():
        with open('cogs/data/command_stats.json', 'r') as command_counter:
            command_stats = json.load(command_counter)
            command_counter.close()

        return command_stats

    # Dump the command statistics to json file
    @staticmethod
    def write_command_stats(command_stats):
        with open('cogs/data/command_stats.json', 'w') as command_counter:
            json.dump(command_stats, command_counter, indent=4)
            command_counter.close()

    # Checks if bot has permission to use external emojis in the guild, returns external emoji if permitted
    # otherwise, returns the fallback emoji
    @staticmethod
    async def use_emoji(ctx, external_emoji, fallback_emoji):
        perms = ctx.channel.permissions_for(ctx.guild.me)

        if perms.use_external_emojis:
            return external_emoji

        else:
            return fallback_emoji


def setup(bot):
    bot.add_cog(Events(bot))
