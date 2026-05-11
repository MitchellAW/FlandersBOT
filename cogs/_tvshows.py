from abc import abstractmethod
from tkinter import FALSE

import compuglobal
import discord
from discord.app_commands import AppCommandError, CommandOnCooldown
from discord.ext import commands

from cogs.events import Events


class TVShowCog(commands.Cog):
    def __init__(self, bot, api: compuglobal.AsyncCompuGlobalAPI):
        self.bot = bot
        self.api = api
        self.api_cache = {}

        self.api_title = type(self.api).__name__.lower()

    # Load the api cache for this show
    async def cog_load(self):
        if "masterofallscience" not in self.api_title and (self.api_cache is None or len(self.api_cache.keys()) == 0):
            self.api_cache = await self.build_cache()

    # Handle slash command cooldowns for tv shows
    async def cog_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, CommandOnCooldown):
            await interaction.response.send_message(
                ":hourglass: Sorry, command on cooldown. Please slow diddly-ding-dong down.", ephemeral=True
            )

    async def build_cache(self) -> dict[str, compuglobal.EpisodeSummary]:
        episodes: list[compuglobal.EpisodeSummary] = await self.api.navigator()
        return {episode.key: episode for episode in episodes}

    # Format error to not embed links on page status error
    @staticmethod
    def format_error(error):
        return str(error).replace("http", "<http").replace(".com/", ".com/>")

    @staticmethod
    def get_unique_results(search_results: list[compuglobal.Frame]):
        unique = {}

        # Filter out similar results
        unique_results = []
        for result in search_results:
            check = unique.get(result.key)

            if check is None or abs(check.timestamp - result.timestamp) > 50000:
                unique.update({result.key: result})
                unique_results.append(result)

        return unique_results

    # Get random or searched screencap based on search parameter and update cached_screencaps
    async def get_screencap(self, ctx, search=None):
        screencap = None
        try:
            if search is None:
                screencap = await self.api.get_random_screencap()

            else:
                screencap = await self.api.search_for_screencap(search)

            self.bot.cached_screencaps.update({ctx.message.channel.id: screencap})

        except compuglobal.APIPageStatusError as error:
            await ctx.send(self.format_error(error))

        except compuglobal.NoSearchResultsFound as error:
            await ctx.send(error)

        return screencap

    # Post a random screencap image with caption
    async def post_image(self, ctx, search=None, caption=None):
        try:
            screencap = await self.get_screencap(ctx, search)

            if screencap is not None:
                await ctx.send(await self.api.get_comic_strip_url(screencap))

        except compuglobal.APIPageStatusError as error:
            await ctx.send(self.format_error(error))

    # Post a gif, if generating, post generating loading message and then edit message to include gif with the
    # generated url
    async def post_gif(self, ctx, search=None, caption=None, generate=True):
        screencap = None
        try:
            screencap = await self.get_screencap(ctx, search)

        except compuglobal.APIPageStatusError as error:
            await ctx.send(self.format_error(error))

        if screencap is not None:
            comic_url = await self.api.get_comic_strip_url(screencap)

            if generate:
                emoji = await Events.use_emoji(ctx, "<a:loading:410316176510418955>", "⌛")
                sent = await ctx.send(f"Generating {screencap.frame.key}... {emoji}")

                try:
                    generated_url = await self.api.get_gif_url(screencap)
                    await sent.edit(content=generated_url)

                except compuglobal.APIPageStatusError as error:
                    await sent.edit(content=self.format_error(error))

                except discord.NotFound:
                    pass

            else:
                await ctx.send(comic_url)

    async def build_gif(self, interaction: discord.Interaction, search: str):
        try:
            search_results = await self.api.search(search)
            unique_results = self.get_unique_results(search_results)

            state = TVReferenceState(frames=unique_results[:25], api=self.api, api_cache=self.api_cache)

            # Get top 25 results
            options = []
            for i in range(min(25, len(unique_results))):
                options.append(SearchResult(unique_results[i], i + 1, self.api_title, state))

            options[0].default = True

            # Create the view containing our dropdown and preview
            gif_builder_view = GifBuilderView(options, state, await state.get_preview_embed())

            # Sending a message containing our gif builder view
            await interaction.response.send_message(view=gif_builder_view, ephemeral=True)

            # Pre-cache desired screencaps from search results
            await state.populate()

        except compuglobal.NoSearchResultsFound:
            await interaction.response.send_message("⚠️ No search results found.", ephemeral=True)


class ContentView(discord.ui.LayoutView):
    def __init__(self, content_url: str, header_text: str, header_url: str, footer_text: str):
        super().__init__()
        self.content_url = content_url

        container = discord.ui.Container()

        header = discord.ui.TextDisplay(content=f"## **[{header_text}]({header_url})**")
        container.add_item(header)

        gallery = discord.ui.MediaGallery()
        gallery.add_item(media=self.content_url)
        container.add_item(gallery)

        footer = discord.ui.TextDisplay(content=f"-# {footer_text}")
        container.add_item(footer)

        self.add_item(container)


class TVReferenceState:
    def __init__(
        self,
        frames: list[compuglobal.Frame],
        api: compuglobal.AsyncCompuGlobalAPI,
        api_cache: dict[str, compuglobal.EpisodeSummary],
    ):
        self.frames = frames
        self.api = api
        self.api_cache = api_cache
        self.gif_builder = None
        self.custom_subtitles: list[compuglobal.Subtitle] | None = None

        self._index = 0
        self.screencaps: dict[compuglobal.Frame, compuglobal.Screencap] = {}

    def set_index(self, index):
        if index < 0 or index > len(self.frames):
            raise ValueError(f"Index {index} is out of bounds, must be between 0-{len(self.frames)}")

        self._index = index

    async def get_frame(self):
        return self.frames[self._index]

    async def get_screencap(self) -> compuglobal.Screencap:
        frame = self.frames[self._index]

        screencap = self.screencaps.get(frame)

        if screencap is None:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)

        return screencap

    async def populate(self):
        for frame in self.frames:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)
            self.screencaps.update({frame: screencap})

    async def get_preview_embed(self):
        screencap = await self.get_screencap()
        view_url = await self.api.get_comic_strip_url(screencap, self.custom_subtitles)
        return view_url

    async def get_embed(self) -> discord.Embed:
        screencap = await self.get_screencap()
        embed = discord.Embed(
            title=f"{screencap.frame.key}: {screencap.episode.title} " f"({screencap.get_real_timestamp()})",
            url=screencap.episode.wiki_link,
        )

        return embed

    async def get_subtitles(self) -> list[compuglobal.Subtitle]:
        screencap = await self.get_screencap()
        return self.custom_subtitles if self.custom_subtitles is not None else screencap.subtitles

    async def get_comic_strip_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_comic_strip_url(screencap, subtitles=subtitles)

    async def get_gif_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_gif_url(screencap, subtitles=subtitles)

    async def get_comic_strip_view(self) -> ContentView:
        screencap = await self.get_screencap()
        comic_url = await self.get_comic_strip_url()
        header_text = f"{screencap.frame.key} - {screencap.episode.title} ({screencap.get_real_timestamp()})"
        api_name = type(self.api).__name__
        footer_text = f"Generated by mitchaw | [View on {api_name}]({comic_url})"
        return ContentView(
            content_url=comic_url,
            header_text=header_text,
            header_url=screencap.episode.wiki_link,
            footer_text=footer_text,
        )

    async def get_gif_view(self) -> ContentView:
        screencap = await self.get_screencap()
        gif_url = await self.get_gif_url()
        api_name = type(self.api).__name__
        header_text = f"{screencap.frame.key} - {screencap.episode.title} ({screencap.get_real_timestamp()})"
        footer_text = f"Generated by mitchaw | [View on {api_name}]({gif_url})"
        return ContentView(
            content_url=gif_url,
            header_text=header_text,
            header_url=screencap.episode.wiki_link,
            footer_text=footer_text,
        )

    async def get_total_duration(self) -> int:
        subtitles = await self.get_subtitles()
        start_timestamp = min(subtitle.start_timestamp for subtitle in subtitles)
        end_timestamp = max(subtitle.end_timestamp for subtitle in subtitles)
        return end_timestamp - start_timestamp


class GifBuilderView(discord.ui.LayoutView):
    def __init__(self, options: list[discord.SelectOption], state: TVReferenceState, image_url: str):
        super().__init__()
        self.state = state

        self.gallery = discord.ui.MediaGallery()
        self.gallery.add_item(media=image_url)
        self.add_item(self.gallery)

        # Add the search results dropdown
        action_row = discord.ui.ActionRow()
        action_row.add_item(SearchResultDropdown(options, state))
        self.add_item(action_row)

        # Add the customisation and post content buttons
        action_row = discord.ui.ActionRow()
        action_row.add_item(GenerateGifButton(state))
        action_row.add_item(GenerateComicButton(state))
        action_row.add_item(CustomiseCaptionButton(state))
        self.add_item(action_row)

    def update_image(self, image_url: str):
        self.gallery.clear_items()
        self.gallery.add_item(media=image_url)


class SearchResult(discord.SelectOption):
    def __init__(self, frame: compuglobal.Frame, index: int, api_title: str, state: TVReferenceState):
        summary = state.api_cache.get(frame.key)
        title = summary.title if summary is not None else "Unknown Title"
        super().__init__(label=f"{index}. {title}", description=f"{frame.key} - {frame.get_real_timestamp()}")


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption], state: TVReferenceState):
        self.view: GifBuilderView
        self.state = state
        super().__init__(placeholder="Choose the best match...", min_values=1, max_values=1, options=options)

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
        self.view.update_image(await self.state.get_preview_embed())
        await interaction.edit_original_response(view=self.view)


class GenerateButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, state: TVReferenceState):
        self.view: GifBuilderView
        self.state = state
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Disable comic/gif builder view elements
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

        content_view = await self.get_content_view()
        if original is not None:
            await original.edit(content=None, view=content_view)

    @abstractmethod
    async def get_content_view(self) -> ContentView:
        pass


class GenerateComicButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Generate Comic", style=discord.ButtonStyle.success, state=state)

    async def get_content_view(self):
        return await self.state.get_comic_strip_view()


class GenerateGifButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        super().__init__(label="Generate Gif", style=discord.ButtonStyle.primary, state=state)

    async def get_content_view(self):
        return await self.state.get_gif_view()


class CustomiseCaptionButton(GenerateButton):
    def __init__(self, state: TVReferenceState):
        self.state = state
        super().__init__(state=state, label="Edit Captions", style=discord.ButtonStyle.secondary)

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


class CustomiseCaptionModal(discord.ui.Modal, title="Customise caption:"):
    def __init__(
        self, total_duration: int, state: TVReferenceState, view: GifBuilderView, subtitles: list[compuglobal.Subtitle]
    ):
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
                required=True,
                max_length=150,
            )
            self.add_item(custom_caption)

        self.merge_caption_checkbox = discord.ui.Checkbox(default=False)
        merge_caption = discord.ui.Label(
            text=f"Combine above captions ({total_duration/1000:.1f} sec)",
            component=self.merge_caption_checkbox,
        )
        self.add_item(merge_caption)

    def get_captions(self):
        for child in self.children:
            if isinstance(child, discord.ui.TextInput):
                yield child.value

    async def get_subtitles(self) -> list[compuglobal.Subtitle]:
        screencap = await self.state.get_screencap()
        return [
            subtitle.model_copy(update={"content": str(new_content)})
            for subtitle, new_content in zip(screencap.subtitles, self.get_captions())
        ]

    async def get_merged_subtitles(self) -> list[compuglobal.Subtitle]:
        subtitles = await self.get_subtitles()

        content = " ".join(subtitle.content for subtitle in subtitles)
        start_timestamp = min(subtitle.start_timestamp for subtitle in subtitles)
        end_timestamp = max(subtitle.end_timestamp for subtitle in subtitles)

        return [
            subtitle.model_copy(
                update={"content": content, "start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
            )
            for subtitle in subtitles
        ]

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=FALSE)

        self.state.custom_subtitles = (
            await self.get_merged_subtitles() if self.merge_caption_checkbox.value else await self.get_subtitles()
        )

        # Update image/comic preview
        self.view.update_image(await self.state.get_preview_embed())
        await interaction.edit_original_response(view=self.view)
