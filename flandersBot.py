import asyncio
import config
import discord
import infoimport asyncio
import config
import discord
import botInfo

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


from cartoons import CartoonAPI
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))
client = discord.Client()

# Create APIs for simpsons, futurama and rick & morty
frinkiac = CartoonAPI('simpsons', 'https://frinkiac.com/')
morbotron = CartoonAPI('futurama', 'https://morbotron.com/')
masterOfAllScience = CartoonAPI('rickandmorty', 'https://masterofallscience.com/')

@bot.event
async def on_ready():
    print('FlandersBOT Logged in.')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))
    print(('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id='
           + client.user.id + '&scope=bot&permissions=19456'))


@bot.command(pass_context=True)
async def shutdown(ctx):
    if ctx.message.author.id == config.OWNERID:
        await bot.say("Shutting down. Bye!")
        await bot.logout()
        await bot.close()



    # If corrent prefix and the message author isn't a bot, check if command
    # was executed
    if prefixFound and not message.author.bot:

        # Shuts the bot down - only usable by the bot owner specified in config
        if message.content.startswith('shutdown') and message.author.id == config.OWNERID:
            await client.send_message(message.channel, 'Shutting down. Bye!')
            await client.logout()
            await client.close()

        # Messages a random Simpsons quote with accompanying gif
        elif message.content.startswith('simpsonsgif'):
            await client.send_message(message.channel, await frinkiac.getRandomCartoon(True))

        # Searches for a Simpsons quote using all text following the command
        # and sends the full quote with accompanying picture
        elif message.content.startswith('simpsons') and len(message.content) > 9:
            await client.send_message(message.channel, await frinkiac.findCartoonQuote(message.content, True))

        # Messages a random Simpsons quote with accompanying picture
        elif message.content.startswith('simpsons'):
            await client.send_message(message.channel, await frinkiac.getRandomCartoon())

        # Messages a random Simpsons quote with accompanying gif
        elif message.content.startswith('futuramagif'):
            await client.send_message(message.channel, await morbotron.getRandomCartoon(True))

        # Searches for a Futurama quote using all text following the command
        # and sends the full quote with accompanying picture
        elif message.content.startswith('futurama') and len(message.content) > 9:
            await client.send_message(message.channel, await morbotron.findCartoonQuote(message.content, True))

        # Messages a random Futurama quote with accompanying picture
        elif message.content.startswith('futurama'):
            await client.send_message(message.channel, await morbotron.getRandomCartoon())

        # Messages a random Simpsons quote with a`ccompanying gif
        elif message.content.startswith('rickandmortygif'):
            await client.send_message(message.channel, await masterOfAllScience.getRandomCartoon(True))

        # Searches for a Rick and Morty quote using all text following the command
        # and sends the full quote with accompanying picture
        elif message.content.startswith('rickandmorty') and len(message.content) > 12:
            await client.send_message(message.channel, await masterOfAllScience.findCartoonQuote(message.content, True))

        # Messages a random Rick and Morty quote with accompanying picture
        elif message.content.startswith('rickandmorty'):
            await client.send_message(message.channel, await masterOfAllScience.getRandomCartoon())

        # Sends a personal message containing the commands
        elif message.content.startswith('help'):
            await client.send_message(message.author, info.commandsList)

        # Sends a personal message containing information regarding the bot
        elif message.content.startswith('info'):
            await client.send_message(message.author, (info.botInfo + '\nServers: ' + str(len(client.servers))))

client.run(config.TOKEN)
