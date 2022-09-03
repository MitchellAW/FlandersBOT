import json
import os

import discord
from discord.ext import commands

import compuglobal
from cogs.events import Events


API_CACHE = {}

# Load all bot extensions from cogs folder
for file in os.listdir("cogs/cache"):
    if file.endswith(".json") and not file.startswith('_'):
        with open(f'cogs/cache/{file}', 'r') as cache_file:
            API_CACHE.update({
                file[:-5]: json.load(cache_file)
            })


class TVShowCog(commands.Cog):
    def __init__(self, bot, api: compuglobal.aio.CompuGlobalAPI):
        self.bot = bot
        self.api = api

        self.api_title = type(self.api).__name__.lower()

    # Format error to not embed links on page status error
    @staticmethod
    def format_error(error):
        return str(error).replace('http', '<http').replace('.com/', '.com/>')

    @staticmethod
    def get_unique_results(search_results: list[compuglobal.Frame]):
        unique = {}

        # Filter out similar results
        unique_results = []
        for result in search_results:
            check = unique.get(result.key)

            if check is None or abs(check.timestamp - result.timestamp) > 50000:
                unique.update({
                    result.key: result
                })
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

            self.bot.cached_screencaps.update(
                {ctx.message.channel.id: screencap}
            )

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
                await ctx.send(await screencap.get_meme_url(caption))

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
            gif_url = await screencap.get_gif_url(caption)

            if generate:
                emoji = await Events.use_emoji(ctx, '<a:loading:410316176510418955>', '⌛')
                sent = await ctx.send(f'Generating {screencap.key}... {emoji}')

                try:
                    generated_url = await self.api.generate_gif(gif_url)
                    await sent.edit(content=generated_url)

                except compuglobal.APIPageStatusError as error:
                    await sent.edit(content=self.format_error(error))

                except discord.NotFound:
                    pass

            else:
                await ctx.send(gif_url)

    async def build_gif(self, interaction: discord.Interaction, search: str):
        try: 
            search_results = await self.api.search(search)
            unique_results = self.get_unique_results(search_results)

            state = TVReferenceState(frames=unique_results[:25], api=self.api)

            # Get top 25 results
            options = []
            for i in range(min(25, len(unique_results))):
                options.append(SearchResult(unique_results[i], i + 1, self.api_title))

            options[0].default = True

            # Create the view containing our dropdown and preview
            gif_builder_view = GifBuilderView(options, state)
            preview = await state.get_preview_embed()

            # Sending a message containing our gif builder view
            await interaction.response.send_message(embed=preview, view=gif_builder_view, ephemeral=True)

            # Pre-cache desired screencaps from search results
            await state.populate()
        
        except compuglobal.NoSearchResultsFound:
            await interaction.response.send_message('⚠️ No search results found.', ephemeral=True)
            


class TVReferenceState:
    def __init__(self, frames: list[compuglobal.Frame], api: compuglobal.aio.CompuGlobalAPI):
        self.frames = frames
        self.api = api
        self.gif_builder = None

        self._index = 0
        self.screencaps = {}

    def set_index(self, index):
        if index < 0 or index > len(self.frames):
            raise ValueError(f'Index {index} is out of bounds, must be between 0-{len(self.frames)}')

        self._index = index

    async def get_frame(self):
        return self.frames[self._index]

    async def get_screencap(self):
        frame = self.frames[self._index]

        if frame in self.screencaps:
            screencap = self.screencaps.get(frame)

        else:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)

        return screencap

    async def populate(self):
        for frame in self.frames:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)
            self.screencaps.update({
                frame: screencap
            })

    async def get_preview_embed(self):
        screencap = await self.get_screencap()
        api_title = type(self.api).__name__.lower()
        view_url = f'https://{api_title}.com/caption/{screencap.key}/{screencap.timestamp}'
        preview_embed = discord.Embed(colour=discord.Colour(0x44981e), 
                                      title=f'{screencap.title} ({screencap.frame.get_real_timestamp()})', 
                                      description=f'{screencap.caption}', url=view_url)
        preview_embed.set_image(url=screencap.frame.image_url)
        return preview_embed

    async def get_gif_embed(self, caption):
        screencap = await self.get_screencap()
        formatted_caption = self.api.format_caption(caption=caption, max_lines=10, max_chars=26, shorten=False)

        gif_embed = discord.Embed(title=f'{screencap.key}: {screencap.title} '
                                        f'({screencap.get_real_timestamp()})', url=screencap.wiki_url)

        # Retry Gif Generation 3 times, this can stall a long time
        for _ in range(3):
            try:
                # Only call API for gif the once
                gif_url = await screencap.get_gif_url(caption=formatted_caption)

                # Generate the gif
                generated_url = await self.api.generate_gif(gif_url)
                gif_embed.set_image(url=generated_url)
                return gif_embed

            # Pass errors
            except compuglobal.APIPageStatusError:
                pass

        return gif_embed


class CustomiseCaptionModal(discord.ui.Modal, title='Add Caption'):
    def __init__(self, state: TVReferenceState, view: discord.ui.View):
        self.state = state
        self.view = view

        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        custom_caption = str(self.children[0])
        screencap = await self.state.get_screencap()
        await interaction.response.defer(thinking=False, ephemeral=False)
        emoji = await Events.use_emoji(interaction, '<a:loading:410316176510418955>', '⌛')
        original = await interaction.channel.send(f'Generating {screencap.key}... {emoji}')

        # Generate gif and get embed
        gif_embed = await self.state.get_gif_embed(custom_caption)
        user = interaction.user
        gif_embed.set_footer(text=f'Generated by {user.name}#{user.discriminator}', icon_url=user.avatar)

        if original is not None:
            await original.edit(content='', embed=gif_embed)

        try:
            # Disable generate gif button and dropdown once gif has been generated
            for child in self.view.children:
                if isinstance(child, discord.ui.Button):
                    child.label = 'Gif Generated'
                    child.style = discord.ButtonStyle.success
                child.disabled = True
                await interaction.edit_original_response(view=self.view)
            
            # Delete gif generation view if not dismissed yet
            await interaction.delete_original_response()
            
        except discord.NotFound:
            pass

    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=False)


class SearchResult(discord.SelectOption):
    def __init__(self, frame: compuglobal.Frame, index: int, api_title: str):
        cache = API_CACHE.get(api_title)
        title = cache.get(frame.key)['Title']
        super().__init__(label=f'{index}. {title}', description=f'{frame.key} - {frame.get_real_timestamp()}')


class SearchResultDropdown(discord.ui.Select):
    def __init__(self, options: list[SearchResult], state: TVReferenceState):
        self.state = state
        super().__init__(placeholder='Choose the best match...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_index = 0
        for i in range(len(self.options)):
            if self.options[i].value == self.values[0]:
                selected_index = i
                self.options[i].default = True
            else:
                self.options[i].default = False

        # Update selected index state
        self.state.set_index(selected_index)

        # Send preview
        embed = await self.state.get_preview_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)


class GifBuilderView(discord.ui.View):
    def __init__(self, options: list[SearchResult], state: TVReferenceState):
        super().__init__()
        self.state = state

        # Adds the dropdown to our view object.
        self.add_item(SearchResultDropdown(options, state))
        self.add_item(GenerateGifButton(state))


class GenerateGifButton(discord.ui.Button):
    def __init__(self, state: TVReferenceState):
        self.state = state
        super().__init__(label='Generate Gif', style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        modal = CustomiseCaptionModal(self.state, self.view)
        screencap = await self.state.get_screencap()

        custom_caption = discord.ui.TextInput(
            label='Enter your caption here:',
            default=screencap.caption[:150],
            style=discord.TextStyle.long,
            placeholder='Enter your caption...',
            required=True,
            max_length=150,
        )
        modal.add_item(custom_caption)
        try:
            await interaction.response.send_modal(modal)

        except Exception as e:
            print(e)
