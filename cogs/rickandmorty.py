import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class RickAndMorty():
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = CartoonAPI('https://masterofallscience.com/')

    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, *, message : str=None):
        if message is None:
            await self.bot.say(await self.masterOfAllScience.
                               getRandomCartoon())

        else:
            await self.bot.say(await self.masterOfAllScience.
                               findCartoonQuote(message, True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self):
        await self.bot.say(await self.masterOfAllScience.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(RickAndMorty(bot))