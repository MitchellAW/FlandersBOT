from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.cartoons import CartoonAPI


class ThirtyRock:
    def __init__(self, bot):
        self.bot = bot
        self.thirty_rock = CartoonAPI('https://goodgodlemon.com/')

    # Messages a random 30 Rock quote with img if no search terms are given,
    # Otherwise, search for 30 Rock quote using search terms and post gif
    @commands.command(aliases=['30rock', '30Rock', '30ROCK'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def thirtyrock(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.thirty_rock.post_image(ctx)

        else:
            await self.thirty_rock.post_gif(ctx, search_terms)

    # Messages a random 30 Rock quote with accomanying gif
    @commands.command(aliases=['30rockgif', '30RockGif', '30ROCKGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def thirtyrockgif(self, ctx):
        await self.thirty_rock.post_gif(ctx)


def setup(bot):
    bot.add_cog(ThirtyRock(bot))

