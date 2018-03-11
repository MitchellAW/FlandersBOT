from compuglobal import MasterOfAllScience
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class RickAndMorty(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, MasterOfAllScience())

    # Messages a random R & M quote with gif if no search terms are given,
    # Otherwise, search for R & M quote using search terms and post gif
    @commands.command(aliases=['ram', 'ramgif', 'rickandmortygif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def rickandmorty(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(RickAndMorty(bot))
