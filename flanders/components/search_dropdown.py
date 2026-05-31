from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import compuglobal
import discord

if TYPE_CHECKING:
    from flanders.models import TVReferenceState


class SearchResult(discord.SelectOption):
    def __init__(self, frame: compuglobal.Frame, index: int, state: TVReferenceState):
        summary = state.api_cache.get(frame.key)
        title = summary.title if summary is not None else "Unknown Title"
        super().__init__(label=f"{index}. {title}", description=f"{frame.key} - {frame.get_real_timestamp()}")


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, options: Sequence[discord.SelectOption], state: TVReferenceState):
        self.state = state
        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=list(options))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected_index = 0
        for i in range(len(self.options)):
            if self.options[i].value == self.values[0]:
                selected_index = i
                self.options[i].default = True
            else:
                self.options[i].default = False

        # Update selected index state
        self.state.set_index(selected_index)
        if self.view is not None:
            self.view.update_image(await self.state.get_comic_strip_url())
            await interaction.edit_original_response(view=self.view)
