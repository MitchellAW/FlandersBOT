import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands

class Futurama():
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    @commands.command()
    async def futurama(self, *, message : str=None):
        if message == None:
            await self.bot.say(await self.morbotron.getRandomCartoon())

        else:
            await self.bot.say(await self.morbotron.findCartoonQuote(message,
                                                                     True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    async def futuramagif(self, ):
        await self.bot.say(await self.morbotron.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(Futurama(bot))

