import asyncio
import botInfo
import config
import discord

from cartoons import CartoonAPI
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))
bot.remove_command('help')

# Create APIs for simpsons, futurama and rick & morty
frinkiac = CartoonAPI('simpsons', 'https://frinkiac.com/')
morbotron = CartoonAPI('futurama', 'https://morbotron.com/')
masterOfAllScience = CartoonAPI('rickandmorty',
                                'https://masterofallscience.com/')

@bot.event
async def on_ready():
    print('FlandersBOT Logged in.')
    print('Username: ' + str(bot.user.name))
    print('Client ID: ' + str(bot.user.id))
    print(('Invite URL: '
           + 'https://discordapp.com/oauth2/authorize?&client_id='
           + bot.user.id + '&scope=bot&permissions=19456'))

# Prevent bot from replying to other bots and make commands case-insensitive
@bot.event
async def on_message(message):
    if message.author.bot == False:
        message.content = message.content.lower()
        await bot.process_commands(message)

# Whispers a description of the bot with author, framework, server count etc.
@bot.command()
async def info():
    await bot.whisper(botInfo.botInfo + '\nServers: ' + str(len(bot.servers)))

# Whispers a list of the bot commands
@bot.command()
async def help():
    await bot.whisper(botInfo.commandsList)

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

# Shuts the bot down - only usable by the bot owner specified in config
@bot.command(pass_context=True)
async def shutdown(ctx):
    if ctx.message.author.id == config.OWNERID:
        await bot.whisper("Shutting down. Bye!")
        await bot.logout()
        await bot.close()

bot.run(config.TOKEN)
