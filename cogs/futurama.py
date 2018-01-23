import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Futurama():
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, *, message : str=None):
        if message is None:
            await self.bot.say(await self.morbotron.getRandomCartoon())

        else:
            await self.bot.say(await self.morbotron.findCartoonQuote(message,
                                                                     True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ):
        await self.bot.say(await self.morbotron.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(Futurama(bot))

