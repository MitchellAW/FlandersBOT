from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.tvshows import Frinkiac
from cogs.tvshow import TVShowCog


class Simpsons(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Frinkiac())

    # Messages a random Simpsons quote with img if no search terms are given,
    # Otherwise, search for Simpsons quote using search terms and post gif
    @commands.command(aliases=['Simpsons', 'SIMPSONS'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def simpsons(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.post_image(ctx)

        else:
            await self.post_gif(ctx, search_terms)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Simpsonsgif', 'SimpsonsGif', 'SIMPSONSGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def simpsonsgif(self, ctx):
        await self.post_gif(ctx)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['smeme', 'Smeme', 'SMEME', 'SimpsonsMEME',
                               'SimpsonsMeme', 'SIMPSONSMEME'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def simpsonsmeme(self, ctx, *, search_terms: str):
        await self.post_custom_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(Simpsons(bot))
