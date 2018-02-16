from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.cartoons import CartoonAPI


class RickAndMorty:
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = CartoonAPI('https://masterofallscience.com/')

    # Generate the gif and send it once the generation completes
    async def send_gif(self, ctx, gif_url):
        sent = await ctx.send('Generating... <a:loading:410316176510418955>')
        generated_url = await self.masterOfAllScience.generate_gif(gif_url)
        await sent.edit(content=generated_url)

    @commands.command(aliases=['Rickandmorty', 'RickAndMorty', 'RICKANDMORTY',
                               'ram', 'Ram', 'RAM'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, message: str=None):
        if message is None:
            await ctx.send(await self.masterOfAllScience.get_random_cartoon())

        else:
            gif_url = await self.masterOfAllScience.find_cartoon_quote(message,
                                                                       True)
            if 'https://' not in gif_url:
                await ctx.send(gif_url)

            else:
                await self.send_gif(ctx, gif_url)

    # Messages a random simpsons quote with accomanying gif
    @commands.command(aliases=['Rickandmortygif', 'RickAndMortyGif',
                               'RICKANDMORTYGIF', 'ramgif',
                               'Ramgif', 'RamGif', 'RAMGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self, ctx):
        gif_url = await self.masterOfAllScience.get_random_cartoon(True)
        await self.send_gif(ctx, gif_url)


def setup(bot):
    bot.add_cog(RickAndMorty(bot))
