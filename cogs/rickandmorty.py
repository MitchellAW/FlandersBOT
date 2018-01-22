import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands

class RickAndMorty():
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = CartoonAPI('https://masterofallscience.com/')

    @commands.command()
    async def rickandmorty(self, *, message : str=None):
        if message == None:
            await self.bot.say(await self.masterOfAllScience.
                               getRandomCartoon())

        else:
            await self.bot.say(await self.masterOfAllScience.
                               findCartoonQuote(message, True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    async def rickandmortygif(self):
        await self.bot.say(await self.masterOfAllScience.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(RickAndMorty(bot))
