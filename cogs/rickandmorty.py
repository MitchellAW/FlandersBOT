import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class RickAndMorty():
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = CartoonAPI('https://masterofallscience.com/')

    @commands.command(aliases=['Rickandmorty', 'RICKANDMORTY'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.masterOfAllScience.
                               getRandomCartoon())

        else:
            await ctx.send(await self.masterOfAllScience.
                               findCartoonQuote(message, True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Rickandmortygif', 'RICKANDMORTYGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self, ctx):
        await ctx.send(await self.masterOfAllScience.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(RickAndMorty(bot))
