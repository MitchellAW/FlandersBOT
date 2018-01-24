import aiohttp
import asyncio
import botInfo
import discord
import prefixes
import settings.config
guild
from discord.ext import commands

# Get the prefixes for the bot
async def getPrefix(bot, message):
    extras = await prefixes.prefixesFor(message.guild)
    return commands.when_mentioned_or(*extras)(bot, message)

# Post guild count to update count at https://discordbots.org/
async def updateGuildCount(bot):
    dbUrl = "https://discordbots.org/api/bots/" + str(bot.user.id) + "/stats"
    dbHeaders = {"Authorization" : settings.config.DBTOKEN}
    dbPayload = {"server_count"  : len(bot.guilds)}

    async with aiohttp.ClientSession() as aioClient:
        resp = await aioClient.post(dbUrl, data=dbPayload, headers=dbHeaders)
        print(await resp.text())

    status = discord.Game(name='ned help | {} servers'.
                          format(len(bot.guilds)), type=0)

    await bot.change_presence(game=status, afk=True)

startupExtensions = [
    'cogs.general', 'cogs.simpsons', 'cogs.futurama', 'cogs.rickandmorty',
    'cogs.owner'
    ]

bot = commands.Bot(command_prefix=getPrefix)
bot.remove_command('help')

# Print bot information once bot has started
@bot.event
async def on_ready():
    print('FlandersBOT Logged in.')
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    print(('Invite URL: '
           + 'https://discordapp.com/oauth2/authorize?&client_id='
           + str(bot.user.id) + '&scope=bot&permissions=19456'))

    await updateGuildCount(bot)

# Update guild count on join
@bot.event
async def on_guild_join(guild):
    await updateGuildCount(bot)

# Update guild count on leave
@bot.event
async def on_guild_remove(guild):
    await updateGuildCount(bot)

# Prevent bot from replying to other bots
@bot.event
async def on_message(message):
    if message.author.bot == False:
        ctx = await bot.get_context(message)
        await bot.invoke(ctx)

# Commands error handler, only handles cooldowns at the moment
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandOnCooldown):
       await ctx.send(':hourglass: Command on cooldown. ' +
                      'Slow diddly-ding-dong down.')

    else:
        print(error)

# Load an extension
@bot.command()
async def load(extensionName : str):
    try:
        bot.load_extension(extensionName)

    except (AttributeError, ImportError) as e:
        print("py\n{}: {}\n".format(type(e).__name__, str(e)))
        return

# Unload an extension
@bot.command()
async def unload(extensionName : str):
    bot.unload_extension(extensionName)

# Load all bot cogs
if __name__ == "__main__":
    for extension in startupExtensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(settings.config.TOKEN)
