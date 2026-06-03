from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from flanders.components.caption_modal import CustomiseCaptionModal

if TYPE_CHECKING:
    from flanders.models import TVReferenceState


class CustomiseCaptionButton(discord.ui.Button):
    def __init__(self, state: TVReferenceState):
        self.state = state
        super().__init__(label="Edit Captions", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.view is not None:
            subtitles = await self.state.get_subtitles()
            duration = await self.state.get_total_duration()
            modal = CustomiseCaptionModal(
                total_duration=duration, state=self.state, view=self.view, subtitles=subtitles
            )

            try:
                await interaction.response.send_modal(modal)

            except Exception as e:
                print(e)
