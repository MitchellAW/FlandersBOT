from compuglobal import Morbotron
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class Futurama(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Morbotron())

    # Messages a random Futurama quote with gif if no search terms are given,
    # Otherwise, search for Futurama quote using search terms and post gif
    @commands.command(aliases=['futuramagif', 'fgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def futurama(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(Futurama(bot))
