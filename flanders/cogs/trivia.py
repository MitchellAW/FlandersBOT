import asyncio
from datetime import datetime, timedelta, timezone
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from flanders.bot import FlandersBOT
from flanders.components import (
    TriviaLeaderboardView,
    TriviaPrivacyView,
    TriviaScoreboardView,
    TriviaUserStatsView,
    TriviaView,
)
from flanders.models import (
    FuturamaTrivia,
    SimpsonsTrivia,
    TriviaLeaderboardType,
    TriviaMatch,
)
from flanders.utils import TriviaDB


class Trivia(commands.GroupCog, name="trivia", description="All commands related to trivia!"):
    def __init__(self, bot):
        self.bot: FlandersBOT = bot
        self.trivia_db = TriviaDB(db=self.bot.db)

        self.matches_in_progress: dict[int, TriviaMatch] = {}

    @app_commands.command(name="start", description="Starts a trivia match with questions from the chosen category.")
    @app_commands.describe(category="The television category to use for the trivia questions.")
    @app_commands.checks.cooldown(1, 120.0, key=lambda i: (i.guild_id, i.user.id))
    async def start_trivia(self, interaction: discord.Interaction, category: Literal["The Simpsons", "Futurama"]):
        if interaction.guild_id is None or interaction.channel is None:
            await interaction.response.send_message(
                content="Sorry, trivia can only be played in a server text channel", ephemeral=True
            )
            return None

        if interaction.channel.id in self.matches_in_progress:
            in_progress = self.matches_in_progress.get(interaction.channel.id)
            if in_progress is not None:
                await interaction.response.send_message(
                    content="There is already a trivia match in progress in this channel!"
                    f"\n[Click here]({in_progress.jump_url}) to view the match.",
                    ephemeral=True,
                )
                return None

        if category == "The Simpsons":
            trivia_category = SimpsonsTrivia()
        elif category == "Futurama":
            trivia_category = FuturamaTrivia()
        else:
            trivia_category = SimpsonsTrivia()

        await interaction.response.send_message(
            content="Starting a trivia match!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

        match_message = await interaction.original_response()

        # Load question data from trivia file
        questions = trivia_category.load_questions()

        # Insert new trivia match into DB
        match_id = await self.trivia_db.insert_match(guild_id=interaction.guild_id, category=trivia_category)

        # Continue playing trivia until exit or out of questions
        trivia_match = TriviaMatch(
            host=interaction.user.id,
            match_id=match_id,
            category=trivia_category,
            questions=questions,
            jump_url=match_message.jump_url,
        )

        self.matches_in_progress.update({interaction.channel.id: trivia_match})

        while not trivia_match.is_finished:
            # Insert new trivia round into DB
            trivia_round = trivia_match.start_round()
            if trivia_round is None:
                return

            end_time = datetime.now(tz=timezone.utc) + timedelta(seconds=trivia_category.TIMER_DURATION)
            question_view = TriviaView(trivia_category=trivia_category, trivia_match=trivia_match, end_time=end_time)
            await interaction.edit_original_response(
                content=None,
                view=question_view,
                allowed_mentions=discord.AllowedMentions.none(),
            )

            trivia_question = trivia_round.question

            round_id = await self.trivia_db.insert_round(
                match_id=trivia_match.match_id, question_index=trivia_question.id
            )

            await asyncio.sleep(trivia_category.TIMER_DURATION)

            trivia_match.end_round()

            if trivia_round.total_answers == 0:
                trivia_match.end_match_due_to_inactivity()

            answers = trivia_round.answers
            for answer in answers:
                await self.trivia_db.insert_answer(round_id, answer)

            answer_view = TriviaView(trivia_category=trivia_category, trivia_match=trivia_match, end_time=end_time)
            await interaction.edit_original_response(
                content=None,
                view=answer_view,
                allowed_mentions=discord.AllowedMentions.none(),
            )

            # Set round as complete (Triggers leaderboard stat updates)
            await self.trivia_db.complete_round(round_id)

        # Set the match as complete (Triggers leaderboard stat updates)
        await self.trivia_db.complete_match(match_id=match_id)

        # Remove from active matches if not force stopped already
        if interaction.channel.id in self.matches_in_progress:
            self.matches_in_progress.pop(interaction.channel.id, None)

        await asyncio.sleep(trivia_category.TIMER_DURATION / 2)
        scoreboard = await self.trivia_db.get_scoreboard(match_id)
        scoreboard_view = TriviaScoreboardView(scoreboard=scoreboard, trivia_category=trivia_category)
        await interaction.edit_original_response(
            content=None, view=scoreboard_view, allowed_mentions=discord.AllowedMentions.none()
        )

    @app_commands.command(name="stop", description="Stops any trivia match in progress in this channel.")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    async def stop_trivia(self, interaction: discord.Interaction):
        if interaction.channel is None:
            await interaction.response.send_message("No trivia matches are in progress here.", ephemeral=True)

        else:
            guild_owner_id = interaction.guild.owner_id if interaction.guild is not None else None

            match = self.matches_in_progress.get(interaction.channel.id)
            if match is None or match.is_finished:
                await interaction.response.send_message("No trivia matches are in progress here.", ephemeral=True)

            elif interaction.user.id not in (match.host, guild_owner_id):
                await interaction.response.send_message(
                    "Sorry, you are not the host of this trivia match or the server owner.", ephemeral=True
                )

            else:
                match.force_end_match()
                await interaction.response.send_message(
                    "The trivia match will end once the current round ends.", ephemeral=True
                )
                self.matches_in_progress.pop(interaction.channel.id)

    @app_commands.command(name="stats", description="Shows all of your trivia statistics.")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    async def trivia_stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_stats = await self.trivia_db.get_user_stats(interaction.user.id)
        if user_stats is None:
            await interaction.edit_original_response(content="Sorry, I was unable to find any statistics for you.")
        else:
            user_stats_view = TriviaUserStatsView(user_stats=user_stats, user=interaction.user)
            await interaction.edit_original_response(
                view=user_stats_view,
                allowed_mentions=discord.AllowedMentions.none(),
            )

    @app_commands.command(name="leaderboard", description="Shows the trivia leaderboard for many categories.")
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    async def trivia_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Get some miscellaneous statistics for the footer
        leader_count = await self.trivia_db.get_leaderboard_user_count()
        match_count = await self.trivia_db.get_match_count()
        round_count = await self.trivia_db.get_round_count()

        stats = [stat for stat in TriviaLeaderboardType]

        avatar = self.bot.user.avatar if self.bot.user is not None else None
        avatar_url = avatar.url if avatar is not None else None

        scorers: dict[TriviaLeaderboardType, list[tuple[str, int]]] = {}
        if leader_count >= 1:
            for stat in stats:
                scorers.update({stat: await self.trivia_db.get_leaderboard_results(stat, limit=10)})

        footer = f"{leader_count:,} participants, {round_count:,} questions answered, across {match_count:,} matches."

        view = TriviaLeaderboardView(leaderboard=scorers, footer=footer, thumbnail_url=avatar_url)
        await interaction.edit_original_response(view=view)

    @app_commands.command(name="privacy", description="Adjust your privacy settings.")
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
    async def privacy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        current_setting = await self.trivia_db.get_user_privacy_setting(interaction.user.id)
        current_setting = current_setting if current_setting is not None else 1

        view = TriviaPrivacyView(privacy_setting=current_setting, trivia_db=self.trivia_db)
        await interaction.edit_original_response(view=view)


async def setup(bot):
    await bot.add_cog(Trivia(bot))
