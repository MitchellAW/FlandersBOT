import random

import compuglobal
import discord
from compuglobal import AsyncCompuGlobalAPI, Frinkiac, Morbotron
from discord import app_commands
from discord.ext import commands

from flanders.bot import FlandersBOT
from flanders.models import TVReferenceState
from flanders.ui import BuilderView


class TVShowCog(commands.Cog):
    def __init__(self, bot: FlandersBOT) -> None:
        self.bot = bot
        self.api_cache: dict[str, dict[str, compuglobal.EpisodeSummary]] = {}

    # Load the api cache for this show
    async def cog_load(self) -> None:
        all_apis = [Frinkiac(session=self.bot.session), Morbotron(session=self.bot.session)]
        for api in all_apis:
            if self.api_cache.get(api.TITLE) is None:
                self.api_cache.update({api.TITLE: await self.build_cache(api)})

    async def get_cache(self, api: AsyncCompuGlobalAPI) -> dict[str, compuglobal.EpisodeSummary]:
        cache = self.api_cache.get(api.TITLE)
        if cache is None:
            cache = await self.build_cache(api)
            self.api_cache.update({api.TITLE: cache})

        return cache

    async def build_cache(self, api: AsyncCompuGlobalAPI) -> dict[str, compuglobal.EpisodeSummary]:
        episodes: list[compuglobal.EpisodeSummary] = await api.navigator()
        return {episode.key: episode for episode in episodes}

    @app_commands.command(name="simpsons", description="Posts a matching gif from The Simpsons using Frinkiac.")
    @app_commands.describe(search="Search by quote (e.g. nothing at all)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_simpsons_gif(self, interaction: discord.Interaction, search: str) -> None:
        frinkiac = Frinkiac(session=self.bot.session)
        await self.build_gif(interaction, frinkiac, search)

    @app_commands.command(name="steamedhams", description="Posts a random gif from the iconic steamed hams skit.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def post_steamed_hams(self, interaction: discord.Interaction) -> None:
        frinkiac = Frinkiac(session=self.bot.session)

        # Steamed hams episode key
        steamed_hams_key = "S07E21"

        # The middle timestamp of the skit  (start: 483532, end: 652200)
        middle_timestamp = 567866

        # Show bot thinking while hams are steamed
        await interaction.response.defer(ephemeral=False, thinking=False)

        # Get all frames for the steamed hams skit
        # Skit duration is 2:48 (168 seconds), get frames 80 seconds before and 80 seconds after mid point
        # 4 seconds are subtracted from start and end to allow for 7 second gif length and prevent displaying parts of
        # other skits
        frames = await frinkiac.get_frames(steamed_hams_key, middle_timestamp, 80000, 80000)

        # Check frames are returned
        if len(frames) > 0:
            steamed_ham = random.choice(frames)  # noqa: S311
            screencap = await frinkiac.get_screencap(episode=steamed_hams_key, timestamp=steamed_ham.timestamp)

            # Ensure valid screencap
            if screencap is not None:
                # Post the generated gif
                generated_url = await frinkiac.get_gif_url(screencap)
                await interaction.edit_original_response(content=generated_url)

    @app_commands.command(name="futurama", description="Posts a matching gif from Futurama using Morbotron.")
    @app_commands.describe(search="Search by quote (e.g. shut up and take my money)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_futurama_gif(self, interaction: discord.Interaction, search: str) -> None:
        morbotron = Morbotron(session=self.bot.session)
        await self.build_gif(interaction, morbotron, search)

    @app_commands.command(
        name="rickandmorty",
        description="Posts a matching gif from Rick and Morty using MasterOfAllScience.",
    )
    @app_commands.describe(search="Search by quote (e.g. you pass butter)")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def build_rick_and_morty_gif(self, interaction: discord.Interaction, search: str) -> None:  # noqa: ARG002 - Deprecated
        down_message = "Sorry, <https://masterofallscience.com> is down at the moment."
        await interaction.response.send_message(down_message, ephemeral=True)

    def get_unique_results(self, search_results: list[compuglobal.FrameResult]) -> list[compuglobal.FrameResult]:
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

    async def build_gif(self, interaction: discord.Interaction, api: AsyncCompuGlobalAPI, search: str) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            search_results = await api.search(search)
            unique_results = self.get_unique_results(search_results)

            channel_id = interaction.channel.id if interaction.channel is not None else None

            cache = await self.get_cache(api)

            state = TVReferenceState(
                bot=self.bot,
                frames=unique_results[:25],
                api=api,
                api_cache=cache,
                channel=channel_id,
            )

            # Create the view containing our dropdown and preview
            transcript = await state.get_transcript()
            gif_builder_view = BuilderView(unique_results, transcript, state, await state.get_comic_strip_url())

            # Sending a message containing our gif builder view
            await interaction.edit_original_response(content=None, view=gif_builder_view)

        except compuglobal.NoSearchResultsFoundError:
            await interaction.edit_original_response(content="⚠️ No search results found.")


async def setup(bot: FlandersBOT) -> None:
    await bot.add_cog(TVShowCog(bot))
