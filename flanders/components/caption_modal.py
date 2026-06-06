from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from collections.abc import Generator

    import compuglobal

    from flanders.components.builder_view import BuilderView
    from flanders.models import TVReferenceState


class CustomiseCaptionModal(discord.ui.Modal, title="Customise caption:"):
    def __init__(
        self,
        total_duration: int,
        state: TVReferenceState,
        view: BuilderView,
        subtitles: list[compuglobal.Subtitle],
    ) -> None:
        super().__init__()
        self.state = state
        self.view = view

        labels = ["first", "second", "third", "fourth", "fifth"]

        for i, subtitle in enumerate(subtitles):
            duration = subtitle.end_timestamp - subtitle.start_timestamp
            seconds = duration / 1000
            custom_caption = discord.ui.TextInput(
                label=f"Customise {labels[i]} caption ({seconds:.1f} sec):",
                default=subtitle.content,
                style=discord.TextStyle.short,
                placeholder="Enter your caption...",
                required=False,
                max_length=150,
            )
            self.add_item(custom_caption)

        self.merge_caption_checkbox = discord.ui.Checkbox(default=False)
        merge_caption = discord.ui.Label(
            text=f"Combine above captions ({total_duration / 1000:.1f} sec)",
            component=self.merge_caption_checkbox,
        )
        self.add_item(merge_caption)

    def get_captions(self) -> Generator[str]:
        for child in self.children:
            if isinstance(child, discord.ui.TextInput):
                yield child.value

    async def get_subtitles(self) -> list[compuglobal.Subtitle]:
        screencap = await self.state.get_screencap()
        return [
            subtitle.model_copy(update={"content": new_content})
            for subtitle, new_content in zip(screencap.subtitles, self.get_captions(), strict=True)
        ]

    async def get_merged_subtitles(self) -> list[compuglobal.Subtitle]:
        subtitles = await self.get_subtitles()

        content = " ".join(subtitle.content for subtitle in subtitles)
        start_timestamp = min(subtitle.start_timestamp for subtitle in subtitles)
        end_timestamp = max(subtitle.end_timestamp for subtitle in subtitles)

        return [
            subtitle.model_copy(
                update={"content": content, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp},
            )
            for subtitle in subtitles
        ]

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        self.state.custom_subtitles = (
            await self.get_merged_subtitles() if self.merge_caption_checkbox.value else await self.get_subtitles()
        )

        # Update image/comic preview
        self.view.update_image(await self.state.get_comic_strip_url())
        await interaction.edit_original_response(view=self.view)
