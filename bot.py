import datetime
import json

import discord
from discord.ext import commands

import api.bot_lists
import api.compuglobal
import prefixes
import settings.config


# Get the prefixes for the bot
def get_prefix(bot, message):
    extras = prefixes.prefixes_for(message.guild, bot.prefix_data)
    return commands.when_mentioned_or(*extras)(bot, message)


# All cogs that will be loaded on bots startup
startup_extensions = [
    'cogs.general', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty',
    'cogs.thirtyrock', 'cogs.westwing', 'cogs.owner', 'cogs.trivia'
    ]


class FlandersBOT(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix)

        self.remove_command('help')
        self.command_stats = self.read_command_stats()
        self.status_format = 'Ned help | {} Servers'
        self.prefix_data = prefixes.read_prefixes()
        self.uptime = datetime.datetime.utcnow()

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
            ctx = await self.get_context(message)
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

        elif isinstance(error, api.compuglobal.APIPageStatusError):
            await ctx.send(error)

        elif isinstance(error, api.compuglobal.NoSearchResultsFound):
            await ctx.send(error)

        else:
            print(error)

    # Update guild count at https://discordbots.org and in bots status/presence
    async def update_status(self):
        await api.bot_lists.update_guild_count(self, 'https://bots.discord.pw/',
                                               settings.config.BD_TOKEN)
        await api.bot_lists.update_guild_count(self, 'https://discordbots.org/',
                                               settings.config.DB_TOKEN)
        status = discord.Game(name=self.status_format.format(len(self.guilds)),
                              type=0)
        await self.change_presence(game=status, afk=False)

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
