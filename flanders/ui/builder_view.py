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

        # Add the search results dropdown
        self.add_item(discord.ui.ActionRow(SearchResultDropdown(self.unique_results, state=self.state)))

        # Add the preview image
        self.gallery = discord.ui.MediaGallery()
        self.gallery.add_item(media=self.image_url)
        self.add_item(self.gallery)

        # Add customisable subtitle timing dropdown
        self.timestamp_row = discord.ui.ActionRow(TimingDropdown(self.transcript, state=self.state))

        # Add the customisation and post content buttons
        self.button_row = discord.ui.ActionRow(
            GenerateGifButton(self.state),
            GenerateComicButton(self.state),
            CustomiseCaptionButton(self.state),
            ToggleTimingButton(),
        )
        self.add_item(self.button_row)

        if self.state.user_prefs.advanced_mode:
            self.toggle_timing_dropdown()

    async def update_image(self) -> None:
        self.image_url = await self.state.get_comic_strip_url()
        self.gallery.clear_items()
        self.gallery.add_item(media=self.image_url)

    async def update_timestamp_dropdown(self) -> None:
        transcript = await self.state.get_transcript()
        self.timestamp_row.clear_items()
        self.timestamp_row.add_item(TimingDropdown(transcript=transcript, state=self.state))

    def toggle_timing_dropdown(self) -> None:
        self.show_timing = not self.show_timing
        if self.show_timing:
            self.remove_item(self.button_row)
            self.add_item(self.timestamp_row)
            self.add_item(self.button_row)

        else:
            self.remove_item(self.timestamp_row)

    async def show_summary(
        self,
        interaction: discord.Interaction,
        summary: str,
        content_url: str | None = None,
    ) -> None:
        self.clear_items()
        summary += f"\n[View Content Here]({content_url})" if content_url is not None else ""
        self.add_item(discord.ui.TextDisplay(content=f"{summary}"))

        # Keep the buttons as they will need to edit response again
        if content_url is None:
            for button in self.button_row.walk_children():
                if isinstance(button, discord.ui.Button):
                    button.disabled = True
            self.add_item(self.button_row)

        await interaction.edit_original_response(view=self)


class CustomiseCaptionButton(discord.ui.Button):
    def __init__(self, state: TVReferenceState) -> None:
        self.state = state
        emoji = "<:edit:1512642373597794344>"
        super().__init__(emoji=emoji, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None or not isinstance(self.view, BuilderView):
            msg = "Button must be added to a BuilderView before its callback can be invoked"
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
        self.is_toggled = False

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None or not isinstance(self.view, BuilderView):
            msg = "Button must be added to a BuilderView before its callback can be invoked"
            raise ValueError(msg)

        self.is_toggled = not self.is_toggled
        self.style = discord.ButtonStyle.success if self.is_toggled else discord.ButtonStyle.secondary

        await interaction.response.defer(ephemeral=True)
        self.view.toggle_timing_dropdown()
        await interaction.edit_original_response(view=self.view)


class GenerateButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, content_type: str, state: TVReferenceState) -> None:
        self.state = state
        self.content_type = content_type
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None or not isinstance(self.view, BuilderView):
            msg = "Button must be added to a BuilderView before its callback can be invoked"
            raise ValueError(msg)

        await interaction.response.defer(ephemeral=True)
        await self.view.show_summary(interaction, summary=f"Generating {self.content_type}...")

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

        await self.view.show_summary(interaction, summary=summary, content_url=content_url)

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
    def __init__(self, frame: compuglobal.Frame, index: int, state: TVReferenceState, **kwargs) -> None:  # noqa: ANN003
        self.frame = frame
        summary = state.api_cache.get(frame.key)
        title = summary.title if summary is not None else "Unknown Title"
        super().__init__(label=f"{index}. {title}", description=f"{frame.key} - {frame.timecode}", **kwargs)


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, unique_results: list[compuglobal.FrameResult], state: TVReferenceState) -> None:
        self.state = state
        options = [
            SearchResult(unique_result, i + 1, self.state, default=i == 0)
            for i, unique_result in enumerate(unique_results[:10])
        ]
        self.search_options = options
        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=list(options))

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None or not isinstance(self.view, BuilderView):
            msg = "Dropdown must be added to a BuilderView before its callback can be invoked"
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
    def __init__(self, subtitle: compuglobal.Subtitle, **kwargs) -> None:  # noqa: ANN003
        self.subtitle = subtitle
        self.MAX_CHARS = 100

        description = self.shorten_text(subtitle.timecode)
        label = self.shorten_text(subtitle.content)
        super().__init__(label=label, description=description, **kwargs)

    def shorten_text(self, text: str) -> str:
        return f"{text[: self.MAX_CHARS - 3]}..." if len(text) >= self.MAX_CHARS else text[: self.MAX_CHARS]


class TimingDropdown(discord.ui.Select):
    def __init__(self, transcript: list[compuglobal.Subtitle], state: TVReferenceState) -> None:
        self.state = state
        options = [
            TimingOption(
                subtitle,
                default=subtitle.start_timestamp <= self.state.frame_timestamp <= subtitle.end_timestamp,
            )
            for subtitle in transcript
        ]

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
        if self.view is None or not isinstance(self.view, BuilderView):
            msg = "Dropdown must be added to a BuilderView before its callback can be invoked"
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
