import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Futurama():
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.morbotron.getRandomCartoon())

        else:
            await ctx.send(await self.morbotron.findCartoonQuote(message,
                                                                     True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Futuramagif', 'FUTURAMAGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ctx):
        await ctx.send(await self.morbotron.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(Futurama(bot))

