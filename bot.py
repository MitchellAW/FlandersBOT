import json
from datetime import datetime
import sys
import traceback

import asyncio
import asyncpg
import discord
from discord.ext import commands

import api.bot_lists
import prefixes


# Get the prefixes for the bot
def get_prefix(bot, message):
    extras = prefixes.prefixes_for(message.guild, bot.prefix_data)
    return commands.when_mentioned_or(*extras)(bot, message)


# All cogs that will be loaded on bots startup
startup_extensions = [
    'cogs.general', 'cogs.stats', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty', 'cogs.owner', 'cogs.trivia'
    ]

intents = discord.Intents.default()
intents.members = True


class FlandersBOT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True, intents=intents)

        self.remove_command('help')
        self.command_stats = self.read_command_stats()
        self.status_index = 0
        self.bg_task = self.loop.create_task(self.cycle_status_format())
        self.db_conn = None
        self.bg_task_2 = self.loop.create_task(self.track_votes())
        self.status_formats = ['Ned help | {} Servers', 'Ned vote | {} Servers']
        self.prefix_data = prefixes.read_prefixes()
        self.uptime = datetime.utcnow()
        self.LOGGING_CHANNEL = 415700137302818836
        self.cached_screencaps = {}
        self.reminders = []
        self.db = None

        with open('settings/config.json', 'r') as config_file:
            self.config = json.load(config_file)

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(extension, exc))

    # Print bot information, update status and set uptime when bot is ready
    async def on_ready(self):
        print('Username: ' + str(self.user.name))
        print('Client ID: ' + str(self.user.id))
        await self.update_status()
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.utcnow()

        if self.db is None:
            self.db = await asyncpg.create_pool(**self.config['db_credentials'])

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
            await ctx.send(':hourglass: Command on cooldown. Slow diddly-ding-dong down. (' + str(time_left) + 's)',
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
            await logging.send('Command: ' + str(ctx.command.qualified_name))
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
        await api.bot_lists.update_guild_counts(self)
        status = discord.Game(name=self.status_formats[self.status_index].format(len(self.guilds)))
        await self.change_presence(activity=status)

    # Cycle through all status formats, waits a minute between status changes
    async def cycle_status_format(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self.status_index >= len(self.status_formats) - 1:
                self.status_index = 0

            else:
                self.status_index += 1

            status = discord.Game(name=self.status_formats[self.status_index].format(len(self.guilds)))

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
