import discord

from compuglobal.aio import MasterOfAllScience
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from cogs._tvshows import TVShowCog


class RickAndMorty(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, MasterOfAllScience())

    # Messages a random R & M quote with gif if no search terms are given, otherwise, search for R & M quote using
    # search terms and post gif
    @commands.command(aliases=['ram', 'r&m', 'rick', 'morty', 'ramgif', 'rickandmortygif',
                               'masterofallscience', 'masterofall', 'moas'])
    @commands.cooldown(1, 3, BucketType.channel)
    @commands.guild_only()
    async def rickandmorty(self, ctx, *, search_terms: str = None):
        # Handle possible custom captions
        if search_terms is not None and ' | ' in search_terms:
            args = search_terms.split(' | ', 1)
            await self.post_gif(ctx, args[0], args[1])

        # Use default caption
        else:
            await self.post_gif(ctx, search_terms)

    @app_commands.command(name='rickandmorty',
                          description='Posts a matching gif from Rick and Morty using MasterOfAllScience.')
    @app_commands.describe(search='Search by quote (e.g. you pass butter)')
    async def build_rick_and_morty_gif(self, interaction: discord.Interaction, search: str):
        await self.build_gif(interaction, search)


async def setup(bot):
    await bot.add_cog(RickAndMorty(bot))
