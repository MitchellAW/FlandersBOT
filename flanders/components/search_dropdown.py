from __future__ import annotations

from typing import TYPE_CHECKING

import compuglobal
import discord

if TYPE_CHECKING:
    from flanders.models import TVReferenceState


class SearchResult(discord.SelectOption):
    def __init__(self, frame: compuglobal.Frame, index: int, state: TVReferenceState):
        self.frame = frame
        summary = state.api_cache.get(frame.key)
        title = summary.title if summary is not None else "Unknown Title"
        super().__init__(label=f"{index}. {title}", description=f"{frame.key} - {frame.get_real_timestamp()}")


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, options: list[SearchResult], state: TVReferenceState):
        self.search_options = options
        self.state = state
        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=list(options))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        chosen_frame = self.search_options[0].frame
        for search_option, option in zip(self.search_options, self.options, strict=True):
            if option.value == self.values[0]:
                chosen_frame = search_option.frame
                option.default = True
            else:
                option.default = False

        # Update selected frame state
        self.state.set_frame(chosen_frame.key, chosen_frame.timestamp)
        if self.view is not None:
            self.view.update_image(await self.state.get_comic_strip_url())
            await self.view.update_timestamp_dropdown()
            await interaction.edit_original_response(view=self.view)


class TimingOption(discord.SelectOption):
    def __init__(self, subtitle: compuglobal.Subtitle):
        self.subtitle = subtitle
        self.MAX_CHARS = 100

        real_timestamp = compuglobal.Timestamp.get_real_timestamp(subtitle.representative_timestamp)
        description = self.shorten_text(real_timestamp)
        label = self.shorten_text(subtitle.content)
        super().__init__(label=label, description=description)

    def shorten_text(self, text: str) -> str:
        return f"{text[: self.MAX_CHARS - 3]}..." if len(text) >= self.MAX_CHARS else text[: self.MAX_CHARS]


class TimingDropdown(discord.ui.Select):
    def __init__(self, options: list[TimingOption], state: TVReferenceState):
        self.state = state

        options = self.shorten_options(options)
        self.search_options = options

        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=list(options))

    # Find subtitle matching selected timestamp, and return items in a radius either side of it (default: 3)
    def shorten_options(self, options: list[TimingOption], radius: int = 4) -> list[TimingOption]:
        chosen_index = next(
            i
            for i in range(len(options))
            if options[i].subtitle.start_timestamp <= self.state.frame_timestamp <= options[i].subtitle.end_timestamp
        )

        size = radius * 2 + 1
        start = max(0, min(chosen_index - radius, len(options) - size))

        return options[start : start + size]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        chosen_subtitle = self.search_options[0].subtitle
        for search_option, option in zip(self.search_options, self.options, strict=True):
            if option.value == self.values[0]:
                chosen_subtitle = search_option.subtitle
                option.default = True
            else:
                option.default = False

        # Update selected frame state
        self.state.set_frame(chosen_subtitle.key, timestamp=chosen_subtitle.representative_timestamp)
        if self.view is not None:
            self.view.update_image(await self.state.get_comic_strip_url())
            await interaction.edit_original_response(view=self.view)
