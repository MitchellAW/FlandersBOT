import asyncio
import datetime
import json

import aiohttp
import discord
from discord.ext import commands

import api.dbl
import botInfo
import prefixes
import settings.config

# Read the command statistics from json file
def readCommandStats():
    with open('cogs/data/commandStats.json', 'r') as commandCounter:
        commandStats = json.load(commandCounter)
        commandCounter.close()

    return commandStats

# Dump the command statistics to json file
def writeCommandStats(commandStats):
    with open('cogs/data/commandStats.json', 'w') as commandCounter:
        json.dump(commandStats, commandCounter, indent=4)
        commandCounter.close()

# Get the prefixes for the bot
async def getPrefix(bot, message):
    extras = await prefixes.prefixesFor(message.guild, bot.prefixData)
    return commands.when_mentioned_or(*extras)(bot, message)

# Update guild count at discordbots.org and in bots status/presence
async def updateStatus(bot):
    await api.dbl.updateGuildCount(bot)
    status = discord.Game(name=bot.statusFormat.format(len(bot.guilds)), type=0)
    await bot.change_presence(game=status, afk=True)

startupExtensions = [
    'cogs.general', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty',
    'cogs.owner', 'cogs.trivia'
    ]

bot = commands.Bot(command_prefix=getPrefix)
bot.remove_command('help')
bot.commandStats = readCommandStats()
bot.statusFormat = 'Ned help | {} Servers'
bot.prefixData = prefixes.readPrefixes()

# Print bot information once bot has started
@bot.event
async def on_ready():
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    bot.uptime = datetime.datetime.utcnow()
    await updateStatus(bot)

# Update guild count on join
@bot.event
async def on_guild_join(guild):
    await updateStatus(bot)

# Update guild count on leave
@bot.event
async def on_guild_remove(guild):
    await updateStatus(bot)

# Prevent bot from replying to other bots
@bot.event
async def on_message(message):
    if message.author.bot == False:
        ctx = await bot.get_context(message)
        await bot.invoke(ctx)

# Track number of command executed
@bot.event
async def on_command(ctx):
    command = ctx.command.qualified_name
    if command in bot.commandStats:
        bot.commandStats[command] += 1

    else:
        bot.commandStats[command] = 1

    writeCommandStats(bot.commandStats)

# Commands error handler, only handles cooldowns at the moment
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        timeLeft = round(error.retry_after, 2)
        await ctx.send(':hourglass: Command on cooldown. ' +
                       'Slow diddly-ding-dong down. (' + str(timeLeft) +'s)')
    else:
        print(error)

# Load all bot cogs
if __name__ == "__main__":
    for extension in startupExtensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(settings.config.TOKEN)
