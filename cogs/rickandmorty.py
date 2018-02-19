from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.tvshows import TVShowAPI


class RickAndMorty:
    def __init__(self, bot):
        self.bot = bot
        self.masterOfAllScience = TVShowAPI('https://masterofallscience.com/')

    # Messages a random R & M quote with img if no search terms are given,
    # Otherwise, search for R & M quote using search terms and post gif
    @commands.command(aliases=['Rickandmorty', 'RickAndMorty', 'RICKANDMORTY',
                               'ram', 'Ram', 'RAM'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.masterOfAllScience.post_image(ctx)

        else:
            await self.masterOfAllScience.post_gif(ctx, search_terms)

    # Messages a random rick and morty quote with accomanying gif
    @commands.command(aliases=['Rickandmortygif', 'RickAndMortyGif',
                               'RICKANDMORTYGIF', 'ramgif',
                               'Ramgif', 'RamGif', 'RAMGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self, ctx):
        await self.masterOfAllScience.post_gif(ctx)


def setup(bot):
    bot.add_cog(RickAndMorty(bot))
