from __future__ import annotations

from typing import TYPE_CHECKING

import compuglobal
import discord

from flanders.components.caption_button import CustomiseCaptionButton, ToggleTimingButton
from flanders.components.generate_button import GenerateComicButton, GenerateGifButton
from flanders.components.search_dropdown import SearchResult, SearchResultDropdown, TimingDropdown, TimingOption

if TYPE_CHECKING:
    from flanders.models import TVReferenceState


class BuilderView(discord.ui.LayoutView):
    def __init__(self, unique_results, transcript: list[compuglobal.Subtitle], state: TVReferenceState, image_url: str):
        super().__init__(timeout=600)
        self.unique_results = unique_results
        self.transcript = transcript
        self.state = state
        self.image_url = image_url

        self.show_timing = False

        self.summary = discord.ui.TextDisplay(content="")

        self.search_row = discord.ui.ActionRow()

        self.gallery = discord.ui.MediaGallery()

        self.timestamp_row = discord.ui.ActionRow()
        self.button_row = discord.ui.ActionRow()

        # Add the search results dropdown
        dropdown = self.build_search_dropdown(self.unique_results)
        self.search_row.add_item(dropdown)
        self.add_item(self.search_row)

        # Add the preview image
        self.gallery.add_item(media=self.image_url)
        self.add_item(self.gallery)

        # Add customisable subtitle timing dropdown
        timestamp_dropdown = self.build_timestamp_dropdown(self.transcript)
        self.timestamp_row.add_item(timestamp_dropdown)

        # Add the customisation and post content buttons
        self.toggle_timing_button = ToggleTimingButton()
        self.button_row.add_item(GenerateGifButton(self.state))
        self.button_row.add_item(GenerateComicButton(self.state))
        self.button_row.add_item(CustomiseCaptionButton(self.state))
        self.button_row.add_item(self.toggle_timing_button)
        self.add_item(self.button_row)

    def build_search_dropdown(self, unique_results: list[compuglobal.Frame]) -> SearchResultDropdown:
        # Get top 10 results
        options = []
        for i in range(min(10, len(unique_results))):
            options.append(SearchResult(unique_results[i], i + 1, self.state))

        options[0].default = True

        return SearchResultDropdown(options, self.state)

    def build_timestamp_dropdown(self, transcript: list[compuglobal.Subtitle]):
        options = []

        for i in range(len(transcript)):
            option = TimingOption(transcript[i])

            if transcript[i].start_timestamp <= self.state.frame_timestamp <= transcript[i].end_timestamp:
                option.default = True
            options.append(option)

        return TimingDropdown(options, self.state)

    def update_image(self, image_url: str):
        self.image_url = image_url
        self.gallery.clear_items()
        self.gallery.add_item(media=self.image_url)

    async def update_timestamp_dropdown(self) -> None:
        self.timestamp_row.clear_items()
        transcript = await self.state.get_transcript()
        dropdown = self.build_timestamp_dropdown(transcript)
        self.timestamp_row.add_item(dropdown)

    def toggle_timing_dropdown(self) -> None:
        self.show_timing = not self.show_timing
        if self.show_timing:
            self.remove_item(self.button_row)
            self.add_item(self.timestamp_row)
            self.add_item(self.button_row)
            self.toggle_timing_button.style = discord.ButtonStyle.success

        else:
            self.toggle_timing_button.style = discord.ButtonStyle.secondary
            self.remove_item(self.timestamp_row)

    def show_summary(self, summary: str, component: discord.ui.Button, content_url: str | None = None) -> None:
        self.remove_item(self.summary)
        self.summary.content = summary
        self.add_item(self.summary)

        self.remove_item(self.button_row)
        self.remove_item(self.search_row)
        self.remove_item(self.gallery)

        self.button_row.clear_items()

        if content_url is not None:
            self.button_row.add_item(discord.ui.Button(label="View Content", url=content_url))

        component.disabled = True
        self.button_row.add_item(component)

        self.add_item(self.button_row)
