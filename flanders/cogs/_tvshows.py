import compuglobal
import discord
from discord.ext import commands

from flanders.bot import FlandersBOT
from flanders.models import TVReferenceState
from flanders.ui import BuilderView


class TVShowCog(commands.Cog):
    def __init__(self, bot: FlandersBOT, api: compuglobal.AsyncCompuGlobalAPI) -> None:
        self.bot = bot
        self.api = api
        self.api_cache: dict[str, compuglobal.EpisodeSummary] = {}

        self.api_title = type(self.api).__name__.lower()

    # Load the api cache for this show
    async def cog_load(self) -> None:
        if "masterofallscience" not in self.api_title and (self.api_cache is None or len(self.api_cache.keys()) == 0):
            self.api_cache = await self.build_cache()

    async def build_cache(self) -> dict[str, compuglobal.EpisodeSummary]:
        episodes: list[compuglobal.EpisodeSummary] = await self.api.navigator()
        return {episode.key: episode for episode in episodes}

    @staticmethod
    def get_unique_results(search_results: list[compuglobal.FrameResult]) -> list[compuglobal.FrameResult]:
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

    async def build_gif(self, interaction: discord.Interaction, search: str) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            search_results = await self.api.search(search)
            unique_results = self.get_unique_results(search_results)

            channel_id = interaction.channel.id if interaction.channel is not None else None

            state = TVReferenceState(
                bot=self.bot,
                frames=unique_results[:25],
                api=self.api,
                api_cache=self.api_cache,
                channel=channel_id,
            )

            # Create the view containing our dropdown and preview
            top_result = unique_results[0]
            transcript = await self.api.get_transcript(episode=top_result.key, timestamp=top_result.timestamp)
            gif_builder_view = BuilderView(unique_results, transcript, state, await state.get_comic_strip_url())

            # Sending a message containing our gif builder view
            await interaction.edit_original_response(content=None, view=gif_builder_view)

            # Pre-cache desired screencaps from search results
            await state.populate()

        except compuglobal.NoSearchResultsFoundError:
            await interaction.edit_original_response(content="⚠️ No search results found.")
