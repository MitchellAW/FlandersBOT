import aiohttp
import asyncio
import botInfo
import config
import discord
import json

from cartoons import CartoonAPI
from discord.ext import commands

# Get the prefixes for the bot
async def getPrefix(bot, message):
    extras = await prefixesFor(message.server)
    return commands.when_mentioned_or(*extras)(bot, message)

# Get all the prefixes the server can use
async def prefixesFor(serverID):
    return ['ned ', 'ned-', 'diddly-', 'doodly-', 'diddly ', 'doodly ']

# Post server count to update count at https://discordbots.org/
async def updateServerCount(bot):
    dbUrl = "https://discordbots.org/api/bots/" + bot.user.id + "/stats"
    dbHeaders = {"Authorization" : config.DBTOKEN}
    dbPayload = {"server_count"  : len(bot.servers)}

    async with aiohttp.ClientSession() as aioClient:
        await aioClient.post(dbUrl, data=dbPayload, headers=dbHeaders)


bot = commands.Bot(command_prefix=getPrefix)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('FlandersBOT Logged in.')
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    print(('Invite URL: '
           + 'https://discordapp.com/oauth2/authorize?&client_id='
           + bot.user.id + '&scope=bot&permissions=19456'))
    print('Currently active in ' + str(len(bot.servers)) + ' servers')

    await updateServerCount(bot)

# Update server count on join
@bot.event
async def on_server_join(server):
    await updateServerCount(bot)

# Update server count on leave
@bot.event
async def on_server_remove(server):
    await updateServerCount(bot)

# Prevent bot from replying to other bots and make commands case-insensitive
@bot.event
async def on_message(message):
    if message.author.bot == False:
        message.content = message.content.lower()
        await bot.process_commands(message)

# Whispers a description of the bot with author, framework, server count etc.
@bot.command()
async def info():
    await bot.whisper((botInfo.botInfo + '\n***Currently active in '
                      + str(len(bot.servers)) + ' servers***'))

# Whispers a list of the bot commands
@bot.command()
async def help():
    await bot.whisper(botInfo.commandsList)

@bot.command()
async def prefix():
    await bot.say('My command prefixes are `ned `, <@' + bot.user.id +
                  '> , `diddly`, `doodly` (all followed by a space) and ' +
                  ' `diddly-` and `doodly-`')

@bot.command()
async def stats():
    # Get server count
    serverCount = len(bot.servers)

    # Count users online in servers
    totalMembers = 0
    onlineUsers = 0
    for server in bot.servers:
        totalMembers += len(server.members)
        for member in server.members:
            if member.status == discord.Status.online:
                onlineUsers += 1

    # Embed statistics output
    embed = discord.Embed(colour=discord.Colour(0x44981e))

    embed.set_thumbnail(url="https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png")
    embed.set_author(name="FlandersBOT Statistics", url="https://github.com/FlandersBOT", icon_url="https://images.discordapp.net/avatars/221609683562135553/afc35c7bcaf6dcb1c86a1c715ac955a3.png")

    embed.add_field(name="Bot Name", value="FlandersBOT#0680", inline=True)
    embed.add_field(name="Bot Owner", value="Mitch#8293", inline=True)
    embed.add_field(name="Total Members", value=str(totalMembers), inline=True)
    embed.add_field(name="Server Count", value=str(serverCount), inline=True)
    embed.add_field(name="Online Users", value=str(onlineUsers), inline=True)
    embed.add_field(name="Online Users per Server", value=str(onlineUsers / serverCount), inline=True)

    # Post statistics
    await bot.say(embed=embed)

# Searches for a simpsons quote using message following prefix, messages a gif
# of first search result. Messages a random simspons image if no search
# arguments given.
@bot.command()
async def simpsons(*, message : str=None):
    if message == None:
        await bot.say(await frinkiac.getRandomCartoon())

    else:
        await bot.say(await frinkiac.findCartoonQuote(message, True))

# Messages a random simpsons quote with accomanying gif
@bot.command()
async def simpsonsgif():
    await bot.say(await frinkiac.getRandomCartoon(True))

# Searches for a futurama quote using message following prefix, messages a gif
# of first search result. Messages a random futurama image if no search
# arguments given.
@bot.command()
async def futurama(*, message : str=None):
    if message == None:
        await bot.say(await morbotron.getRandomCartoon())

    else:
        await bot.say(await morbotron.findCartoonQuote(message, True))

# Messages a random futurama quote with accomanying gif
@bot.command()
async def futuramagif():
    await bot.say(await morbotron.getRandomCartoon(True))

# Searches for a rick and morty quote using message following prefix, messages
# a gif of first search result. Messages a random rick and morty image if no
# search arguments given.
@bot.command()
async def rickandmorty(*, message : str=None):
    if message == None:
        await bot.say(await masterOfAllScience.getRandomCartoon())

    else:
        await bot.say(await masterOfAllScience.findCartoonQuote(message, True))

# Messages a random rick and morty quote with accomanying gif
@bot.command()
async def rickandmortygif():
    await bot.say(await masterOfAllScience.getRandomCartoon(True))

@bot.command(pass_context=True)
async def serverlist(ctx):
    if ctx.message.author.id == config.OWNERID:
        serverList = ""
        for server in bot.servers:
            serverList += server.name + '\n'
        await bot.whisper(serverList)

# Shuts the bot down - only usable by the bot owner specified in config
@bot.command(pass_context=True)
async def shutdown(ctx):
    if ctx.message.author.id == config.OWNERID:
        await bot.whisper("Shutting down. Bye!")
        await bot.logout()
        await bot.close()

# Create APIs for simpsons, futurama and rick & morty
frinkiac = CartoonAPI('simpsons', 'https://frinkiac.com/')
morbotron = CartoonAPI('futurama', 'https://morbotron.com/')
masterOfAllScience = CartoonAPI('rickandmorty',
                                'https://masterofallscience.com/')

bot.run(config.TOKEN)
