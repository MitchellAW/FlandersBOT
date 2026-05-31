import discord

# pyrefly: ignore [deprecated]
from compuglobal.aio import MasterOfAllScience
from discord import app_commands

from flanders.cogs._tvshows import TVShowCog


class RickAndMorty(TVShowCog):
    DOWN_MESSAGE = "Sorry, <https://masterofallscience.com> is down at the moment."

    def __init__(self, bot):
        super().__init__(bot, MasterOfAllScience(session=bot.session))

    @app_commands.command(
        name="rickandmorty", description="Posts a matching gif from Rick and Morty using MasterOfAllScience."
    )
    @app_commands.describe(search="Search by quote (e.g. you pass butter)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_rick_and_morty_gif(self, interaction: discord.Interaction, search: str):
        await interaction.response.send_message(self.DOWN_MESSAGE, ephemeral=True)


async def setup(bot):
    await bot.add_cog(RickAndMorty(bot))
