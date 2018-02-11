from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import api.bot_lists
from api.cartoons import CartoonAPI


class ThirtyRock:
    def __init__(self, bot):
        self.bot = bot
        self.thirty_rock = CartoonAPI('https://goodgodlemon.com/')

    # Generate the gif and send it once the generation completes
    async def send_gif(self, ctx, gif_url):
        upvoters = await api.bot_lists.get_upvoters()
        if str(ctx.message.author.id) in upvoters:
            sent = await ctx.send('Generating... <a:loading:410316176510418955>')
            generated_url = await self.thirty_rock.generate_gif(gif_url)
            await sent.edit(content=generated_url)

        else:
            await ctx.send(gif_url)

    @commands.command(aliases=['30rock', '30Rock', '30ROCK'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def thirtyrock(self, ctx, *, message: str=None):
        if message is None:
            await ctx.send(await self.thirty_rock.get_random_cartoon())

        else:
            gif_url = await self.thirty_rock.find_cartoon_quote(message, True)
            if 'https://' not in gif_url:
                await ctx.send(gif_url)

            else:
                await self.send_gif(ctx, gif_url)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['30rockgif', '30RockGif', '30ROCKGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def thirtyrockgif(self, ctx):
        gif_url = await self.thirty_rock.get_random_cartoon(True)
        await self.send_gif(ctx, gif_url)


def setup(bot):
    bot.add_cog(ThirtyRock(bot))

