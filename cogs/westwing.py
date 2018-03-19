from compuglobal.aio import CapitalBeatUs
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class WestWing(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, CapitalBeatUs())

    # Messages a random West Wing quote with gif if no search terms are given,
    # Otherwise, search for West Wing quote using search terms and post gif
    @commands.command(aliases=['westwinggif', 'wgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def westwing(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(WestWing(bot))
