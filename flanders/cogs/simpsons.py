import random

import discord
from compuglobal.aio import Frinkiac
from discord import app_commands

from flanders.bot import FlandersBOT
from flanders.cogs._tvshows import TVShowCog


class Simpsons(TVShowCog):
    def __init__(self, bot: FlandersBOT) -> None:
        super().__init__(bot, Frinkiac(session=bot.session))
        self.frinkiac = Frinkiac(session=self.bot.session)

    @app_commands.command(name="simpsons", description="Posts a matching gif from The Simpsons using Frinkiac.")
    @app_commands.describe(search="Search by quote (e.g. nothing at all)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_simpsons_gif(self, interaction: discord.Interaction, search: str) -> None:
        await self.build_gif(interaction, search)

    @app_commands.command(name="steamedhams", description="Posts a random gif from the iconic steamed hams skit.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def post_steamed_hams(self, interaction: discord.Interaction) -> None:
        # Steamed hams episode key
        steamed_hams_key = "S07E21"

        # The middle timestamp of the skit  (start: 483532, end: 652200)
        middle_timestamp = 567866

        # Show bot thinking while hams are steamed
        await interaction.response.defer(ephemeral=False, thinking=False)

        # Get all frames for the steamed hams skit
        # Skit duration is 2:48 (168 seconds), get frames 80 seconds before and 80 seconds after mid point
        # 4 seconds are subtracted from start and end to allow for 7 second gif length and prevent displaying parts of
        # other skits
        frames = await self.frinkiac.get_frames(steamed_hams_key, middle_timestamp, 80000, 80000)

        # Check frames are returned
        if len(frames) > 0:
            steamed_ham = random.choice(frames)  # noqa: S311 - Not cryptographic
            screencap = await self.frinkiac.get_screencap(steamed_hams_key, steamed_ham.timestamp)

            # Ensure valid screencap
            if screencap is not None:
                # Post the generated gif
                generated_url = await self.frinkiac.get_gif_url(screencap)
                await interaction.edit_original_response(content=generated_url)


async def setup(bot: FlandersBOT) -> None:
    await bot.add_cog(Simpsons(bot))
