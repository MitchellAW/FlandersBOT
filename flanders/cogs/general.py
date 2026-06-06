import discord
from discord import app_commands
from discord.ext import commands

from flanders.bot import FlandersBOT


class General(commands.Cog):
    def __init__(self, bot: FlandersBOT) -> None:
        self.bot = bot

    @app_commands.command(name="support", description="Need help or want to suggest improvements for Flanders?")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    async def support(self, interaction: discord.Interaction) -> None:
        support_message = (
            "Hi-diddly-ho, neighborino! I hear you might want some hel-diddly-elp using my features!\n"
            "All are welcome to join the [Flanders Support server!](https://discord.gg/xMmxMYg)\n"
            "Here you can ask questions, or discuss new feature ideas for Flanders.\n"
            "You can also visit the [GitHub repository](<https://github.com/MitchellAW/FlandersBOT>) "
            "if you'd like to post a feature request or issue.\n"
        )
        await interaction.response.send_message(content=support_message, ephemeral=True)


async def setup(bot: FlandersBOT) -> None:
    await bot.add_cog(General(bot))
