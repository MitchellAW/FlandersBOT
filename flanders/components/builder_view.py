from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from flanders.components.caption_button import CustomiseCaptionButton
from flanders.components.generate_button import GenerateComicButton, GenerateGifButton
from flanders.components.search_dropdown import SearchResult, SearchResultDropdown

if TYPE_CHECKING:
    from flanders.models import TVReferenceState


class BuilderView(discord.ui.LayoutView):
    def __init__(self, unique_results, state: TVReferenceState, image_url: str):
        super().__init__()
        self.state = state

        # Add the search results dropdown
        action_row = discord.ui.ActionRow()
        dropdown = self.build_dropdown(unique_results)
        action_row.add_item(dropdown)
        self.add_item(action_row)

        # Add the preview image
        self.gallery = discord.ui.MediaGallery()
        self.gallery.add_item(media=image_url)
        self.add_item(self.gallery)

        # Add the customisation and post content buttons
        action_row = discord.ui.ActionRow()
        action_row.add_item(GenerateGifButton(state))
        action_row.add_item(GenerateComicButton(state))
        action_row.add_item(CustomiseCaptionButton(state))
        self.add_item(action_row)

    def build_dropdown(self, unique_results) -> SearchResultDropdown:
        # Get top 25 results
        options = []
        for i in range(min(25, len(unique_results))):
            options.append(SearchResult(unique_results[i], i + 1, self.state))

        options[0].default = True

        return SearchResultDropdown(options, self.state)

    def update_image(self, image_url: str):
        self.gallery.clear_items()
        self.gallery.add_item(media=image_url)
