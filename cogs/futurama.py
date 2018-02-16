from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.cartoons import CartoonAPI


class Futurama:
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    # Messages a random Futurama quote with img if no search terms are given,
    # Otherwise, search for Futurama quote using search terms and post gif
    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, ctx, *, search_terms : str=None):
        if search_terms is None:
            await self.morbotron.post_image(ctx)

        else:
            await self.morbotron.post_gif(ctx, search_terms)

    # Messages a random Futurama quote with accomanying gif
    @commands.command(aliases=['Futuramagif', 'FUTURAMAGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ctx):
        await self.morbotron.post_gif(ctx)


def setup(bot):
    bot.add_cog(Futurama(bot))

