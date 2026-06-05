import compuglobal
import discord
from discord.ext import commands

from flanders.components import BuilderView
from flanders.models import TVReferenceState


class TVShowCog(commands.Cog):
    def __init__(self, bot, api: compuglobal.AsyncCompuGlobalAPI):
        self.bot = bot
        self.api = api
        self.api_cache: dict[str, compuglobal.EpisodeSummary] = {}

        self.api_title = type(self.api).__name__.lower()

    # Load the api cache for this show
    async def cog_load(self):
        if "masterofallscience" not in self.api_title and (self.api_cache is None or len(self.api_cache.keys()) == 0):
            self.api_cache = await self.build_cache()

    async def build_cache(self) -> dict[str, compuglobal.EpisodeSummary]:
        episodes: list[compuglobal.EpisodeSummary] = await self.api.navigator()
        return {episode.key: episode for episode in episodes}

    # Format error to not embed links on page status error
    @staticmethod
    def format_error(error):
        return str(error).replace("http", "<http").replace(".com/", ".com/>")

    @staticmethod
    def get_unique_results(search_results: list[compuglobal.FrameResult]):
        timestamp_diff_required = 50000
        unique = {}

        # Filter out similar results
        unique_results = []
        for result in search_results:
            check = unique.get(result.key)

            if check is None or abs(check.timestamp - result.timestamp) > timestamp_diff_required:
                unique.update({result.key: result})
                unique_results.append(result)

        return unique_results

    async def build_gif(self, interaction: discord.Interaction, search: str):
        try:
            search_results = await self.api.search(search)
            unique_results = self.get_unique_results(search_results)

            channel_id = interaction.channel.id if interaction.channel is not None else None

            state = TVReferenceState(
                bot=self.bot, frames=unique_results[:25], api=self.api, api_cache=self.api_cache, channel=channel_id
            )

            # Create the view containing our dropdown and preview
            gif_builder_view = BuilderView(unique_results, state, await state.get_comic_strip_url())

            # Sending a message containing our gif builder view
            await interaction.response.send_message(view=gif_builder_view, ephemeral=True)

            # Pre-cache desired screencaps from search results
            await state.populate()

        except compuglobal.NoSearchResultsFoundError:
            await interaction.response.send_message("⚠️ No search results found.", ephemeral=True)
