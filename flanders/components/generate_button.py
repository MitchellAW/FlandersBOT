from abc import abstractmethod

import discord

from flanders.cogs.events import Events
from flanders.components.content_view import TVContentView
from flanders.models import TVReferenceState


class GenerateButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, state: TVReferenceState):
        self.state = state
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Disable comic/gif builder view elements
        if self.view is not None:
            for child in self.view.walk_children():
                if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                    child.disabled = True

            await interaction.edit_original_response(view=self.view)

        # Generate gif
        screencap = await self.state.get_screencap()
        emoji = await Events.use_emoji(interaction, "<a:loading:410316176510418955>", "⌛")

        interaction_channel = interaction.channel

        original = None
        if isinstance(interaction_channel, discord.TextChannel):
            original = await interaction_channel.send(f"Generating {screencap.frame.key}... {emoji}")

        await self.state.cache_screencap()

        content_url = await self.get_content_url()
        content_view = TVContentView(
            content_url=content_url,
            episode_title=screencap.episode.title,
            episode_url=f"{self.state.api.BASE_URL}/episode/{screencap.frame.key}/{screencap.frame.timestamp}",
            episode_details=f"{screencap.frame.key} - {screencap.get_real_timestamp()}",
            author=interaction.user.mention,
        )

        if original is not None:
            await original.edit(content=None, view=content_view, allowed_mentions=discord.AllowedMentions.none())

    @abstractmethod
    async def get_content_url(self) -> str:
        pass


class GenerateComicButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Send Comic", style=discord.ButtonStyle.secondary, state=state)

    async def get_content_url(self):
        return await self.state.get_comic_strip_url()


class GenerateGifButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Send Gif", style=discord.ButtonStyle.primary, state=state)

    async def get_content_url(self):
        return await self.state.get_gif_url()
