from compuglobal.aio import Morbotron
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class Futurama(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Morbotron())

    # Messages a random Futurama quote with gif if no search terms are given, otherwise, search for Futurama quote using
    # search terms and post gif
    @commands.command(aliases=['futuramagif', 'fgif', 'morbotron', 'morbo'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def futurama(self, ctx, *, search_terms: str=None):
        # Handle possible custom captions
        if search_terms is not None and ' | ' in search_terms:
            args = search_terms.split(' | ', 1)
            await self.post_gif(ctx, args[0], args[1])

        # Use default caption
        else:
            await self.post_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(Futurama(bot))
