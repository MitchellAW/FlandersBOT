import datetime
import json

import discord
from discord.ext import commands

import api.bot_lists
import prefixes
import settings.config


# Read the command statistics from json file
def read_command_stats():
    with open('cogs/data/commandStats.json', 'r') as command_counter:
        command_stats = json.load(command_counter)
        command_counter.close()

    return command_stats


# Dump the command statistics to json file
def write_command_stats(command_stats):
    with open('cogs/data/commandStats.json', 'w') as command_counter:
        json.dump(command_stats, command_counter, indent=4)
        command_counter.close()


# Get the prefixes for the bot
async def get_prefix(bot, message):
    extras = await prefixes.prefixes_for(message.guild, bot.prefix_data)
    return commands.when_mentioned_or(*extras)(bot, message)


# Update guild count at https://discordbots.org and in bots status/presence
async def update_status(bot):
    await api.bot_lists.update_guild_count(bot, 'https://bots.discord.pw/',
                                           settings.config.BD_TOKEN)
    await api.bot_lists.update_guild_count(bot, 'https://discordbots.org/',
                                           settings.config.DB_TOKEN)
    status = discord.Game(name=bot.status_format.format(len(bot.guilds)),
                          type=0)
    await bot.change_presence(game=status, afk=True)

startup_extensions = [
    'cogs.general', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty',
    'cogs.owner', 'cogs.trivia'
    ]

bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')
bot.command_stats = read_command_stats()
bot.status_format = 'Ned help | {} Servers'
bot.prefix_data = prefixes.read_prefixes()


# Print bot information once bot has started
@bot.event
async def on_ready():
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    bot.uptime = datetime.datetime.utcnow()
    await update_status(bot)


# Update guild count on join
@bot.event
async def on_guild_join(guild):
    await update_status(bot)


# Update guild count on leave
@bot.event
async def on_guild_remove(guild):
    await update_status(bot)


# Prevent bot from replying to other bots
@bot.event
async def on_message(message):
    if not message.author.bot:
        ctx = await bot.get_context(message)
        await bot.invoke(ctx)


# Track number of command executed
@bot.event
async def on_command(ctx):
    command = ctx.command.qualified_name
    if command in bot.command_stats:
        bot.command_stats[command] += 1

    else:
        bot.command_stats[command] = 1

    write_command_stats(bot.command_stats)


# Commands error handler, only handles cooldowns at the moment
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        time_left = round(error.retry_after, 2)
        await ctx.send(':hourglass: Command on cooldown. ' +
                       'Slow diddly-ding-dong down. (' + str(time_left) + 's)',
                       delete_after=error.retry_after)

    elif isinstance(error, commands.MissingPermissions) and \
            ctx.command.qualified_name is not 'forcestop':
            await ctx.send('<:xmark:411718670482407424> Sorry, you don\'t have '
                           'the permissions riddly-required for ' +
                           'that command-aroo! ')

    else:
        print(error)

# Load all bot cogs
if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(settings.config.TOKEN)
