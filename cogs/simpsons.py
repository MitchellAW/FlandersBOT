import discord

from cogs.api.cartoons import CartoonAPI
from discord.ext import commands

class Simpsons():
    def __init__(self, bot):
        self.bot = bot
        self.frinkiac = CartoonAPI('https://frinkiac.com/')

    @commands.command()
    async def simpsons(self, *, message : str=None):
        if message == None:
            await self.bot.say(await self.frinkiac.getRandomCartoon())

        else:
            await self.bot.say(await self.frinkiac.findCartoonQuote(message,
                                                                    True))

    # Messages a random simpsons quote with accomanying gif
    @commands.command()
    async def simpsonsgif(self):
        await self.bot.say(await self.frinkiac.getRandomCartoon(True))

def setup(bot):
    bot.add_cog(Simpsons(bot))

