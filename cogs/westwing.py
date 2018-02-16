from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.cartoons import CartoonAPI


class WestWing:
    def __init__(self, bot):
        self.bot = bot
        self.west_wing = CartoonAPI('https://capitalbeat.us/')

    # Messages a random West Wing quote with img if no search terms are given,
    # Otherwise, search for West Wing quote using search terms and post gif
    @commands.command(aliases=['Westwing', 'WestWing', 'WESTWING'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def westwing(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.west_wing.post_image(ctx)

        else:
            await self.west_wing.post_gif(ctx, search_terms)

    # Messages a random West Wing quote with accomanying gif
    @commands.command(aliases=['Westwinggif', 'WestWingGif', 'WESTWINGGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def westwinggif(self, ctx):
        await self.west_wing.post_gif(ctx)


def setup(bot):
    bot.add_cog(WestWing(bot))

