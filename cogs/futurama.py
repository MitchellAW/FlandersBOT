from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.compuglobal import Morbotron
from cogs.tvshows import TVShowCog


class Futurama(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Morbotron())

    # Messages a random Futurama quote with gif if no search terms are given,
    # Otherwise, search for Futurama quote using search terms and post gif
    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def futurama(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['fmeme', 'Fmeme', 'FMeme', 'FMEME',
                               'Futuramameme', 'FuturamaMeme', 'FUTURAMAMEME'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def futuramameme(self, ctx, *, search_terms: str):
        await self.post_custom_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(Futurama(bot))
