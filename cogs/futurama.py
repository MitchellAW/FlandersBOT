from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.tvshows import TVShowAPI


class Futurama:
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = TVShowAPI('https://morbotron.com/')

    # Messages a random Futurama quote with img if no search terms are given,
    # Otherwise, search for Futurama quote using search terms and post gif
    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.morbotron.post_image(ctx)

        else:
            await self.morbotron.post_gif(ctx, search_terms)

    # Messages a random Futurama quote with accomanying gif
    @commands.command(aliases=['Futuramagif', 'FUTURAMAGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ctx):
        await self.morbotron.post_gif(ctx)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['fmeme', 'Fmeme', 'FMeme', 'FMEME',
                               'Futuramameme', 'FuturamaMeme', 'FUTURAMAMEME'])
    async def futuramameme(self, ctx, *, search_terms: str):
        await self.morbotron.post_custom_gif(ctx, self.bot, search_terms)


def setup(bot):
    bot.add_cog(Futurama(bot))
