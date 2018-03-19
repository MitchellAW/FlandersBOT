from compuglobal.aio import GoodGodLemon
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class ThirtyRock(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, GoodGodLemon())

    # Messages a random 30 Rock quote with gif if no search terms are given,
    # Otherwise, search for 30 Rock quote using search terms and post gif
    @commands.command(aliases=['30rock', '30rockgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def thirtyrock(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(ThirtyRock(bot))
