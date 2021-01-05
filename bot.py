import json
from datetime import datetime
import sys
import traceback

import asyncio
import asyncpg
import discord
from discord.ext import commands

import api.bot_lists

# All cogs that will be loaded on bots startup
startup_extensions = [
    'cogs.general', 'cogs.stats', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty', 'cogs.owner', 'cogs.trivia',
    'cogs.prefixes'
    ]

intents = discord.Intents.default()
intents.members = True


class FlandersBOT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefixes, case_insensitive=True, intents=intents)

        self.remove_command('help')
        self.command_stats = self.read_command_stats()
        self.status_index = 0
        self.bg_task = self.loop.create_task(self.cycle_status_format())
        self.db_conn = None
        self.bg_task_2 = self.loop.create_task(self.track_votes())
        self.status_formats = ['Ned help | {} Servers', 'Ned vote | {} Servers']
        self.default_prefixes = ['ned', 'diddly', 'doodly']
        self.uptime = datetime.utcnow()
        self.LOGGING_CHANNEL = 415700137302818836
        self.cached_prefixes = {}
        self.cached_screencaps = {}
        self.reminders = []
        self.db = None

        with open('settings/config.json', 'r') as config_file:
            self.config = json.load(config_file)

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                print(f'Failed to load extension {extension}\n{exc}')

    # Print bot information, update status and set uptime when bot is ready
    async def on_ready(self):
        print(f'Username: {self.user.name}')
        print(f'Client ID: {self.user.id}')
        await self.update_status()
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.utcnow()

        if self.db is None:
            self.db = await asyncpg.create_pool(**self.config['db_credentials'])

        await self.cache_prefixes()

    # Update guild count on join
    async def on_guild_join(self, guild):
        await self.update_status()

    # Update guild count on leave
    async def on_guild_remove(self, guild):
        await self.update_status()

    # Prevent bot from replying to other bots
    async def on_message(self, message):
        if not message.author.bot:
            ctx = await bot.get_context(message)
            await self.invoke(ctx)

    # Track number of command executed
    async def on_command(self, ctx):
        command = ctx.command.qualified_name
        if command in self.command_stats:
            self.command_stats[command] += 1

        else:
            self.command_stats[command] = 1

        self.write_command_stats(self.command_stats)

    # Commands error handler
    async def on_command_error(self, ctx, error):

        # Allows us to check for original exceptions raised and sent to CommandInvokeError. If nothing is found.
        # We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Channel in FlandersBOT server for logging errors to
        logging = self.get_channel(self.LOGGING_CHANNEL)

        # Ignore non-existent commands
        if isinstance(error, commands.CommandNotFound):
            return

        # Check if command cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(f':hourglass: Command on cooldown. Slow diddly-ding-dong down. ({time_left}s)',
                           delete_after=max(error.retry_after, 5))

        elif isinstance(error, commands.BotMissingPermissions):
            message = '⛔ Sorry, I do not have the permissions riddly-required for that command-aroo!\nRequires: '

            # List all missing permissions
            for i in range(len(error.missing_perms)):
                message += str(error.missing_perms[i])

                if i < len(error.missing_perms) - 1:
                    message += ', '

            await ctx.send(message)

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

    # Gets all approved prefixes for a particular guild using the message received
    async def get_prefixes(self, bot, message):
        guild_prefixes = self.default_prefixes.copy()
        if message.guild.id in self.cached_prefixes:
            guild_prefixes.extend(self.cached_prefixes[message.guild.id])

        # Note, must sort prefixes from longest to shortest length to account for shorter prefixes
        # being contained in longer prefixes
        guild_prefixes.sort(key=len, reverse=True)

        # Note, must end with zero space separator or else it would read "Ned help" as "Ned"+" help" and ignore it
        separators = [' ', '-', '']
        case_insensitive_prefixes = []

        # Loop through and create different casing variants of each prefix, currently builds the following variants:
        # "ned ", "NED ", Ned ", "ned-", "NED-", "Ned-", "ned", "NED", "Ned"
        for prefix in guild_prefixes:
            for separator in separators:
                # All lowercase prefix
                case_insensitive_prefixes.append(prefix.lower() + separator)

                # All uppercase prefix
                case_insensitive_prefixes.append(prefix.upper() + separator)

                # Capitalise first character
                if len(prefix) > 1:
                    case_insensitive_prefixes.append(prefix[0].upper() + prefix[1:] + separator)

        return commands.when_mentioned_or(*case_insensitive_prefixes)(bot, message)

    # Updates the cached prefixes using a SELECT query, is called when a custom prefix is added/removed
    async def cache_prefixes(self):
        self.cached_prefixes.clear()
        query = '''SELECT guild_id, prefix
                   FROM prefixes
                '''
        rows = await self.db.fetch(query)
        for row in rows:
            self.cached_prefixes.setdefault(row['guild_id'], []).append(row['prefix'])

    # Update guild count at bot listing sites and in bots status/presence
    async def update_status(self):
        await api.bot_lists.update_guild_counts(self)
        status = discord.Game(name=self.status_formats[self.status_index].format(str(len(self.guilds))))
        await self.change_presence(activity=status)

    # Cycle through all status formats, waits a minute between status changes
    async def cycle_status_format(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self.status_index >= len(self.status_formats) - 1:
                self.status_index = 0

            else:
                self.status_index += 1

            status = discord.Game(name=self.status_formats[self.status_index].format(str(len(self.guilds))))

            await self.change_presence(activity=status)
            await asyncio.sleep(60)

    async def track_votes(self):
        self.db_conn = await asyncpg.connect(**self.config['db_credentials'])

        async def vote_listener(*args):
            # Get user_id from payload
            user_id = int(args[0][-1])
            user = self.get_user(user_id)

            # Thank subscribed user for voting
            if user_id in self.reminders:
                await user.send('Thanks for voting! You will now be notified when you can vote again in 12 hours.')

            # Get timestamp of users latest vote
            query = '''SELECT MAX(votedAt) FROM VoteHistory 
                       WHERE userID = $1 AND voteType = 'upvote';
                    '''
            row = await self.db_conn.fetchrow(query, user_id)

            # Calculate seconds until next vote
            time_diff = (datetime.utcnow() - row['max'])
            seconds_remaining = 43200 - time_diff.seconds

            # Wait time remaining (should be 12 hours)
            await asyncio.sleep(seconds_remaining)

            # Notify subscribed user that they are able to vote again.
            if user_id in self.reminders:
                await user.send('<https://discordbots.org/bot/221609683562135553/vote>\n**You can vote now.**')

        # Add listener to db connection for when user votes
        await self.db_conn.add_listener('vote', lambda *args: self.loop.create_task(vote_listener(args)))

    # Checks if bot has permission to use external emojis in the guild, returns external emoji if permitted
    # otherwise, returns the fallback emoji
    async def use_emoji(self, ctx, external_emoji, fallback_emoji):
        perms = ctx.channel.permissions_for(ctx.guild.me)

        if perms.use_external_emojis:
            return external_emoji

        else:
            return fallback_emoji

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


bot = FlandersBOT()

with open('settings/config.json', 'r') as conf:
    config = json.load(conf)

bot.run(config['bot_token'])
