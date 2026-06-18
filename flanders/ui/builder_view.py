from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

import discord

from flanders.ui.content_view import TVContentView

if TYPE_CHECKING:
    from collections.abc import Generator

    import compuglobal

    from flanders.models import TVReferenceState

log = logging.getLogger(__name__)


class BuilderView(discord.ui.LayoutView):
    def __init__(
        self,
        unique_results: list[compuglobal.FrameResult],
        transcript: list[compuglobal.Subtitle],
        state: TVReferenceState,
        image_url: str,
    ) -> None:
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

        if self.state.user_prefs.advanced_mode:
            self.toggle_timing_dropdown()

    def build_search_dropdown(self, unique_results: list[compuglobal.FrameResult]) -> SearchResultDropdown:
        # Get top 10 results
        options = [
            SearchResult(unique_result, i + 1, self.state) for i, unique_result in enumerate(unique_results[:10])
        ]
        options[0].default = True

        return SearchResultDropdown(options, self.state)

    def build_timestamp_dropdown(self, transcript: list[compuglobal.Subtitle]) -> TimingDropdown:
        options = []

        for i in range(len(transcript)):
            option = TimingOption(transcript[i])

            if transcript[i].start_timestamp <= self.state.frame_timestamp <= transcript[i].end_timestamp:
                option.default = True
            options.append(option)

        return TimingDropdown(options, self.state)

    async def update_image(self) -> None:
        self.image_url = await self.state.get_comic_strip_url()
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
        self.remove_item(self.timestamp_row)
        self.remove_item(self.gallery)

        self.button_row.clear_items()

        max_url_size = 512
        if content_url is not None and len(content_url) < max_url_size:
            self.button_row.add_item(discord.ui.Button(label="View Content", url=content_url))

        component.disabled = True
        self.button_row.add_item(component)

        self.add_item(self.button_row)

        if content_url is not None and len(content_url) >= max_url_size:
            new_summary = f"{summary}\n[View Content Here]({content_url})"
            self.show_summary(summary=new_summary, component=component, content_url=None)


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


class GenerateButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, content_type: str, state: TVReferenceState) -> None:
        self.state = state
        self.content_type = content_type
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction) -> None:
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
            episode_url=f"{self.state.api.BASE_URL}/episode/{screencap.key}/{screencap.timestamp}",
            episode_details=f"{screencap.key} - {screencap.timecode}",
            author=interaction.user.mention,
        )

        summary = (
            "Sorry neighborino, I'm noodly-not allowed to talk here.\n"
            "But ding-dong-diddily don't worry, you can check it out below!"
        )

        try:
            supported_channels = (discord.TextChannel, discord.Thread, discord.DMChannel)
            if interaction.channel is not None and isinstance(interaction.channel, supported_channels):
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
    def __init__(self, state: TVReferenceState) -> None:
        super().__init__(label="Send Comic", style=discord.ButtonStyle.secondary, content_type="comic", state=state)

    async def get_content_url(self) -> str:
        return await self.state.get_comic_strip_url()


class GenerateGifButton(GenerateButton):
    def __init__(self, state: TVReferenceState) -> None:
        super().__init__(label="Send Gif", style=discord.ButtonStyle.primary, content_type="gif", state=state)

    async def get_content_url(self) -> str:
        return await self.state.get_gif_url()


class SearchResult(discord.SelectOption):
    def __init__(self, frame: compuglobal.Frame, index: int, state: TVReferenceState) -> None:
        self.frame = frame
        summary = state.api_cache.get(frame.key)
        title = summary.title if summary is not None else "Unknown Title"
        super().__init__(label=f"{index}. {title}", description=f"{frame.key} - {frame.timecode}")


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, options: list[SearchResult], state: TVReferenceState) -> None:
        self.search_options = options
        self.state = state
        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=list(options))

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            msg = "Dropdown must be added to a view before its callback can be invoked"
            raise ValueError(msg)

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
        await self.view.update_image()
        await self.view.update_timestamp_dropdown()
        await interaction.edit_original_response(view=self.view)


class TimingOption(discord.SelectOption):
    def __init__(self, subtitle: compuglobal.Subtitle) -> None:
        self.subtitle = subtitle
        self.MAX_CHARS = 100

        description = self.shorten_text(subtitle.timecode)
        label = self.shorten_text(subtitle.content)
        super().__init__(label=label, description=description)

    def shorten_text(self, text: str) -> str:
        return f"{text[: self.MAX_CHARS - 3]}..." if len(text) >= self.MAX_CHARS else text[: self.MAX_CHARS]


class TimingDropdown(discord.ui.Select):
    def __init__(self, options: list[TimingOption], state: TVReferenceState) -> None:
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

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            msg = "Dropdown must be added to a view before its callback can be invoked"
            raise ValueError(msg)

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
        await self.view.update_image()
        await interaction.edit_original_response(view=self.view)


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
            seconds = subtitle.duration / 1000
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
        await self.view.update_image()
        await interaction.edit_original_response(view=self.view)
