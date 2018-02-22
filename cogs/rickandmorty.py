from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from api.compuglobal import MasterOfAllScience
from cogs.tvshows import TVShowCog


class RickAndMorty(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, MasterOfAllScience())

    # Messages a random R & M quote with gif if no search terms are given,
    # Otherwise, search for R & M quote using search terms and post gif
    @commands.command(aliases=['Rickandmorty', 'RickAndMorty', 'RICKANDMORTY',
                               'ram', 'Ram', 'RAM', 'rickandmortygif',
                               'Rickandmortygif', 'RickAndMortyGif',
                               'RICKANDMORTYGIF', 'ramgif', 'Ramgif',
                               'RamGif', 'RAMGIF'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmorty(self, ctx, *, search_terms: str=None):
        await self.post_gif(ctx, search_terms)

    # Allows for custom captions to go with the gif that's searched for
    @commands.command(aliases=['rammeme', 'RAMmeme', 'RAMMeme', 'RAMMEME',
                               'Rickandmortymeme', 'RickAndMortyMeme',
                               'RICKANDMORTYMEME'])
    @commands.cooldown(1, 3, BucketType.channel)
    async def rickandmortymeme(self, ctx, *, search_terms: str):
        await self.post_custom_gif(ctx, search_terms)


def setup(bot):
    bot.add_cog(RickAndMorty(bot))
