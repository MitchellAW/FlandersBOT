import random

import discord
from compuglobal.aio import Frinkiac
from discord import app_commands

from cogs._tvshows import TVShowCog
from cogs.events import Events


class Simpsons(TVShowCog):
    def __init__(self, bot):
        super().__init__(bot, Frinkiac(session=bot.session))
        self.frinkiac = Frinkiac(session=self.bot.session)

    @app_commands.command(name="simpsons", description="Posts a matching gif from The Simpsons using Frinkiac.")
    @app_commands.describe(search="Search by quote (e.g. nothing at all)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_simpsons_gif(self, interaction: discord.Interaction, search: str):
        await self.build_gif(interaction, search)

    @app_commands.command(name="steamedhams", description="Posts a random gif from the iconic steamed hams skit.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def post_steamed_hams(self, interaction: discord.Interaction):
        # Steamed hams episode key
        steamed_hams_key = "S07E21"

        # The middle timestamp of the skit  (start: 483532, end: 652200)
        middle_timestamp = 567866

        # Send gif generation message, will be later edited to display generated gif url
        emoji = await Events.use_emoji(interaction, "<a:loading:410316176510418955>", "⌛ ")
        await interaction.response.send_message(f"Steaming your hams... {emoji}")

        # Get all frames for the steamed hams skit
        # Skit duration is 2:48 (168 seconds), get frames 80 seconds before and 80 seconds after mid point
        # 4 seconds are subtracted from start and end to allow for 7 second gif length and prevent displaying parts of
        # other skits
        frames = await self.frinkiac.get_frames(steamed_hams_key, middle_timestamp, 80000, 80000)

        # Check frames are returned
        if len(frames) > 0:
            steamed_ham = random.choice(frames)
            screencap = await self.frinkiac.get_screencap(steamed_hams_key, steamed_ham.timestamp)

            # Ensure valid screencap
            if screencap is not None:
                # Generate the gif and replace loading message with generated url
                generated_url = await self.frinkiac.get_gif_url(screencap)
                await interaction.edit_original_response(content=generated_url)


async def setup(bot):
    await bot.add_cog(Simpsons(bot))
