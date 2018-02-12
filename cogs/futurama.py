from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

import api.bot_lists
from api.cartoons import CartoonAPI


class Futurama:
    def __init__(self, bot):
        self.bot = bot
        self.morbotron = CartoonAPI('https://morbotron.com/')

    # Generate the gif and send it once the generation completes
    async def send_gif(self, ctx, gif_url):
        sent = await ctx.send('Generating... <a:loading:410316176510418955>')
        generated_url = await self.morbotron.generate_gif(gif_url)
        await sent.edit(content=generated_url)

    @commands.command(aliases=['Futurama', 'FUTURAMA'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futurama(self, ctx, *, message : str=None):
        if message is None:
            await ctx.send(await self.morbotron.get_random_cartoon())

        else:
            gif_url = await self.morbotron.find_cartoon_quote(message, True)
            if 'https://' not in gif_url:
                await ctx.send(gif_url)

            else:
                await self.send_gif(ctx, gif_url)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Futuramagif', 'FUTURAMAGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def futuramagif(self, ctx):
        gif_url = await self.morbotron.get_random_cartoon(True)
        await self.send_gif(ctx, gif_url)


def setup(bot):
    bot.add_cog(Futurama(bot))

