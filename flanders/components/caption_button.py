from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord

from flanders.components.caption_modal import CustomiseCaptionModal

if TYPE_CHECKING:
    from flanders.models import TVReferenceState

log = logging.getLogger(__name__)


class CustomiseCaptionButton(discord.ui.Button):
    def __init__(self, state: TVReferenceState) -> None:
        self.state = state
        emoji = "<:edit:1512642373597794344>"
        super().__init__(emoji=emoji, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            msg = "Button must be added to a view before its callback can be invoked"
            raise ValueError(msg)

        subtitles = await self.state.get_subtitles()
        duration = await self.state.get_total_duration()
        modal = CustomiseCaptionModal(total_duration=duration, state=self.state, view=self.view, subtitles=subtitles)

        try:
            await interaction.response.send_modal(modal)

        except Exception:
            log.exception("Button could not send caption modal")


class ToggleTimingButton(discord.ui.Button):
    def __init__(self) -> None:
        emoji = "<:advanced:1512642321621979246"
        super().__init__(emoji=emoji, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            msg = "Button must be added to a view before its callback can be invoked"
            raise ValueError(msg)

        await interaction.response.defer(ephemeral=True)
        self.view.toggle_timing_dropdown()
        await interaction.edit_original_response(view=self.view)
