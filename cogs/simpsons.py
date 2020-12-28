import discord
from compuglobal.aio import Frinkiac
from compuglobal.aio import FrinkiHams
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs.tvshows import TVShowCog


class Simpsons(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Frinkiac())
        self.frinkihams = FrinkiHams()

    # Messages a random Simpsons quote with gif if no search terms are given, otherwise, search for Simpsons quote using
    # search terms and post gif
    @commands.command(aliases=['simpsonsgif', 'sgif'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def simpsons(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)

    # Generate a random Steamed Hams gif and post it
    @commands.command(aliases=['steamed', 'aurora', 'borealis'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def steamedhams(self, ctx):
        screencap = await self.frinkihams.get_random_screencap()

        gif_url = await screencap.get_gif_url()
        sent = await ctx.send('Steaming your hams...' + '<a:loading:410316176510418955>')

        generated_url = await self.api.generate_gif(gif_url)
        try:
            await sent.edit(content=generated_url)

        except discord.NotFound:
            pass


def setup(bot):
    bot.add_cog(Simpsons(bot))
