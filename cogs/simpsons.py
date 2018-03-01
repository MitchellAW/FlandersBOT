from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.compuglobal import Frinkiac
from cogs.tvshows import TVShowCog


class Simpsons(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Frinkiac())

    # Messages a random Simpsons quote with gif if no search terms are given,
    # Otherwise, search for Simpsons quote using search terms and post gif
    @commands.command(aliases=['simpsonsgif', 'sgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def simpsons(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['smeme'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def simpsonsmeme(self, ctx, *, search_terms: str):
        await self.post_custom_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(Simpsons(bot))
