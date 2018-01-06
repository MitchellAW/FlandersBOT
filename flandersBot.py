import asyncio
import config
import discord
import commands
import requests

from aiohttp import web
from cartoons import CartoonAPI

client = discord.Client()

# Create APIs for simpsons, futurama and rick & morty
frinkiac = CartoonAPI('simpsons', 'https://frinkiac.com/')
morbotron = CartoonAPI('futurama', 'https://morbotron.com/')
masterOfAllScience = CartoonAPI('rickandmorty', 'https://masterofallscience.com/')

@client.event
async def on_ready():
    print('FlandersBOT Logged in.')
    print('Username: ' + str(client.user.name))
    print('Client ID: ' + str(client.user.id))
    print('Invite URL: ' + 'https://discordapp.com/oauth2/authorize?&client_id=' + client.user.id + '&scope=bot&permissions=0')

@client.event
async def on_message(message):
    # If the message author isn't the bot and the message starts with the
    # command prefix ('!' by default), check if command was executed
    if message.author.id != config.BOTID and message.content.startswith(config.COMMANDPREFIX):
        # Remove prefix and change to lowercase so commands are case-insensitive
        message.content = message.content[1:].lower()

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
            await client.send_message(message.channel, await frinkiac.findCartoonQuote(message.content))

        # Messages a random Simpsons quote with accompanying picture
        elif message.content.startswith('simpsons'):
            await client.send_message(message.channel, await frinkiac.getRandomCartoon())

        # Messages a random Simpsons quote with accompanying gif
        elif message.content.startswith('futuramagif'):
            await client.send_message(message.channel, await morbotron.getRandomCartoon(True))

        # Searches for a Futurama quote using all text following the command
        # and sends the full quote with accompanying picture
        elif message.content.startswith('futurama') and len(message.content) > 9:
            await client.send_message(message.channel, await morbotron.findCartoonQuote(message.content))

        # Messages a random Futurama quote with accompanying picture
        elif message.content.startswith('futurama'):
            await client.send_message(message.channel, await morbotron.getRandomCartoon())

        # Messages a random Simpsons quote with a`ccompanying gif
        elif message.content.startswith('rickandmortygif'):
            await client.send_message(message.channel, await masterOfAllScience.getRandomCartoon(True))

        # Searches for a Rick and Morty quote using all text following the command
        # and sends the full quote with accompanying picture
        elif message.content.startswith('rickandmorty') and len(message.content) > 12:
            await client.send_message(message.channel, await masterOfAllScience.findCartoonQuote(message.content))

        # Messages a random Rick and Morty quote with accompanying picture
        elif message.content.startswith('rickandmorty'):
            await client.send_message(message.channel, await masterOfAllScience.getRandomCartoon())

        # Sends a personal message containing the commands
        elif message.content.startswith('help'):
            await client.send_message(message.author, commands.commandsList)

client.run(config.TOKEN)
