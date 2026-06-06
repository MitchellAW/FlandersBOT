from abc import abstractmethod

import discord

from flanders.components.content_view import TVContentView
from flanders.models import TVReferenceState


class GenerateButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, content_type: str, state: TVReferenceState):
        self.state = state
        self.content_type = content_type
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            msg = "Button must be added to a view before its callback can be invoked"
            raise ValueError(msg)

        await interaction.response.defer(ephemeral=True)
        self.view.show_summary(summary=f"Generating {self.content_type}...", component=self)
        await interaction.edit_original_response(view=self.view)

        # Cache screencap
        screencap = await self.state.get_screencap()
        await self.state.cache_screencap()

        content_url = await self.get_content_url()
        content_view = TVContentView(
            content_url=content_url,
            episode_title=screencap.episode.title,
            episode_url=f"{self.state.api.BASE_URL}/episode/{screencap.frame.key}/{screencap.frame.timestamp}",
            episode_details=f"{screencap.frame.key} - {screencap.get_real_timestamp()}",
            author=interaction.user.mention,
        )

        summary = (
            "Sorry neighborino, I'm noodly-not allowed to talk here.\n"
            "But ding-dong-diddily don't worry, you can check it out with the button below!"
        )

        try:
            if interaction.channel is not None and isinstance(
                interaction.channel, (discord.TextChannel, discord.Thread, discord.DMChannel)
            ):
                await interaction.channel.send(view=content_view, allowed_mentions=discord.AllowedMentions.none())
                summary = f"Generated {self.content_type}."

        except discord.Forbidden:
            try:
                await interaction.followup.send(view=content_view, allowed_mentions=discord.AllowedMentions.none())
                summary = f"Generated {self.content_type}."
            except discord.Forbidden:
                pass

        self.view.show_summary(summary=summary, content_url=content_url, component=self)
        await interaction.edit_original_response(view=self.view)

    @abstractmethod
    async def get_content_url(self) -> str:
        pass


class GenerateComicButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Send Comic", style=discord.ButtonStyle.secondary, content_type="comic", state=state)

    async def get_content_url(self):
        return await self.state.get_comic_strip_url()


class GenerateGifButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Send Gif", style=discord.ButtonStyle.primary, content_type="gif", state=state)

    async def get_content_url(self):
        return await self.state.get_gif_url()
