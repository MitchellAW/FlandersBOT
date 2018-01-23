import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Simpsons():
    def __init__(self, bot):
        self.bot = bot
        self.frinkiac = CartoonAPI('https://frinkiac.com/')

    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def simpsons(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.frinkiac.getRandomCartoon())

        else:
            await ctx.send(await self.frinkiac.findCartoonQuote(message,
                                                                    True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def simpsonsgif(self, ctx):
        await ctx.send(await self.frinkiac.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(Simpsons(bot))

