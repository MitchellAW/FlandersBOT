import datetime
import json

import asyncio
import discord
from discord.ext import commands

import api.bot_lists
import prefixes
import settings.config


# Get the prefixes for the bot
def get_prefix(bot, message):
    extras = prefixes.prefixes_for(message.guild, bot.prefix_data)
    return commands.when_mentioned_or(*extras)(bot, message)


# All cogs that will be loaded on bots startup
startup_extensions = [
    'cogs.general', 'cogs.stats', 'cogs.simpsons', 'cogs.futurama',
    'cogs.rickandmorty', 'cogs.owner', 'cogs.trivia'
    ]


class FlandersBOT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, case_insensitive=True)

        self.remove_command('help')
        self.command_stats = self.read_command_stats()
        self.status_index = 0
        self.bg_task = self.loop.create_task(self.cycle_status_format())
        self.status_formats = ['Ned help | {} Servers', 'Ned vote | {} Servers']
        self.prefix_data = prefixes.read_prefixes()
        self.uptime = datetime.datetime.utcnow()
        self.LOGGING_CHANNEL = 415700137302818836
        self.cached_screencaps = {}

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
            self.uptime = datetime.datetime.utcnow()

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
        logging = self.get_channel(self.LOGGING_CHANNEL)
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(':hourglass: Command on cooldown. Slow '
                           'diddly-ding-dong down. (' + str(time_left) + 's)',
                           delete_after=max(error.retry_after, 1))

        elif isinstance(error, commands.MissingPermissions) and \
                ctx.command.qualified_name is not 'forcestop':
                await ctx.send('<:xmark:411718670482407424> Sorry, '
                               'you don\'t have the permissions '
                               'riddly-required for that command-aroo! ')

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(error)

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.MissingPermissions):
            await logging.send(error)
            await logging.send('Command :' + str(ctx.command.qualified_name))
            await logging.send('Missing Perms: ' + error.missing_perms)

        else:
            await logging.send('Command: ' + str(ctx.command.qualified_name))
            await logging.send(error)
            print(error)

    # Update guild count at https://discordbots.org and in bots status/presence
    async def update_status(self):
        await api.bot_lists.update_guild_count(self, 'https://discord.bots.gg/',
                                               settings.config.BD_TOKEN)
        await api.bot_lists.update_guild_count(self, 'https://discordbots.org/',
                                               settings.config.DB_TOKEN)
        status = discord.Game(name=self.status_formats[self.status_index].
                              format(len(self.guilds)))
        await self.change_presence(activity=status)

    # Cycle through all status formats, waits a minute between status changes
    async def cycle_status_format(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if self.status_index == len(self.status_formats) - 1:
                self.status_index = 0

            else:
                self.status_index += 1

            status = discord.Game(name=self.status_formats[self.status_index].
                                  format(len(self.guilds)))

            await self.change_presence(activity=status)
            await asyncio.sleep(60)

    # Read the command statistics from json file
    @staticmethod
    def read_command_stats():
        with open('cogs/data/commandStats.json', 'r') as command_counter:
            command_stats = json.load(command_counter)
            command_counter.close()

        return command_stats

    # Dump the command statistics to json file
    @staticmethod
    def write_command_stats(command_stats):
        with open('cogs/data/commandStats.json', 'w') as command_counter:
            json.dump(command_stats, command_counter, indent=4)
            command_counter.close()


bot = FlandersBOT()
bot.run(settings.config.TOKEN)
