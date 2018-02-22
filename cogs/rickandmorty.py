from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.compuglobal import MasterOfAllScience
from cogs.tvshow import TVShowCog


class RickAndMorty(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, MasterOfAllScience())

    # Messages a random R & M quote with img if no search terms are given,
    # Otherwise, search for R & M quote using search terms and post gif
    @commands.command(aliases=['Rickandmorty', 'RickAndMorty', 'RICKANDMORTY',
                               'ram', 'Ram', 'RAM'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, search_terms: str=None):
        if search_terms is None:
            await self.post_image(ctx)

        else:
            await self.post_gif(ctx, search_terms)

    # Messages a random rick and morty quote with accomanying gif
    @commands.command(aliases=['Rickandmortygif', 'RickAndMortyGif',
                               'RICKANDMORTYGIF', 'ramgif',
                               'Ramgif', 'RamGif', 'RAMGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortygif(self, ctx):
        await self.post_gif(ctx)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['rmmeme', 'RMmeme', 'RMMeme', 'RMMEME',
                               'Rickandmortymeme', 'RickAndMortyMeme',
                               'RICKANDMORTYMEME'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortymeme(self, ctx, *, search_terms: str):
        await self.post_custom_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(RickAndMorty(bot))
