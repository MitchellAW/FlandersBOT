import discord
from compuglobal.aio import Morbotron
from discord import app_commands

from flanders.cogs._tvshows import TVShowCog


class Futurama(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Morbotron(session=bot.session))

    @app_commands.command(name="futurama", description="Posts a matching gif from Futurama using Morbotron.")
    @app_commands.describe(search="Search by quote (e.g. shut up and take my money)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_futurama_gif(self, interaction: discord.Interaction, search: str):
        await self.build_gif(interaction, search)


async def setup(bot):
    await bot.add_cog(Futurama(bot))
