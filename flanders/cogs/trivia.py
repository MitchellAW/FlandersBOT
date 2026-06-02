import asyncio
from datetime import datetime, timedelta, timezone
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import BucketType

from flanders.components import TriviaScoreboardView, TriviaView
from flanders.models import (
    FuturamaTrivia,
    SimpsonsTrivia,
    TriviaLeaderboardType,
    TriviaMatch,
)
from flanders.utils import TriviaDB


class Trivia(commands.GroupCog, name="trivia", description="All commands related to trivia!"):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_db = TriviaDB(db=self.bot.db)

        self.matches_in_progress: dict[int, TriviaMatch] = {}

    # Display a users trivia stats
    @commands.command(aliases=["mystatistics", "mystat", "triviastat", "triviastats", "triviastatistics"])
    @commands.cooldown(1, 30, BucketType.user)
    async def mystats(self, ctx):
        trivia_stats = await self.trivia_db.get_user_stats(ctx.user.id)

        if trivia_stats is not None:
            embed = discord.Embed(colour=discord.Colour(0x44981E))
            embed.set_author(name=f"Trivia Statistics for {ctx.author}", icon_url=ctx.author.avatar)

            # For all trivia statistics, calculate result, get current rank and add all to embed field
            score = round(trivia_stats["score"], 2)
            embed.add_field(name=f":trophy: Score (#{trivia_stats['score_rank']:,})", value=f"{score:,}", inline=True)

            wins = round(trivia_stats["wins"], 2)
            embed.add_field(name=f":first_place: Wins (#{trivia_stats['wins_rank']:,})", value=f"{wins:,}", inline=True)

            losses = round(trivia_stats["losses"], 2)
            embed.add_field(name=f":poop: Losses (#{trivia_stats['losses_rank']:,})", value=f"{losses:,}", inline=True)

            correct_answers = round(trivia_stats["correct_answers"], 2)
            embed.add_field(
                name=f":white_check_mark: Correct (#{trivia_stats['correct_answers_rank']:,})",
                value=f"{correct_answers:,}",
                inline=True,
            )

            incorrect_answers = round(trivia_stats["incorrect_answers"], 2)
            embed.add_field(
                name=f":no_entry: Incorrect (#{trivia_stats['incorrect_answers_rank']:,})",
                value=f"{incorrect_answers:,}",
                inline=True,
            )

            accuracy = round(correct_answers / (incorrect_answers + correct_answers) * 100.0, 2)
            embed.add_field(name=":bow_and_arrow: Accuracy", value=f"{accuracy:,}%", inline=True)

            fastest_answer = round(trivia_stats["fastest_answer"] / 1000, 3)
            embed.add_field(
                name=f":point_up: Fastest Answer (#{trivia_stats['fastest_answer_rank']:,})",
                value=f"{fastest_answer:,}s",
                inline=True,
            )

            current_streak = round(trivia_stats["current_streak"], 2)
            embed.add_field(
                name=f":chart_with_upwards_trend: Current Streak (#{trivia_stats['current_streak_rank']:,})",
                value=f"{current_streak:,}",
                inline=True,
            )

            longest_streak = round(trivia_stats["longest_streak"], 2)
            embed.add_field(
                name=f":four_leaf_clover: Longest Streak (#{trivia_stats['longest_streak_rank']:,})",
                value=f"{longest_streak:,}",
                inline=True,
            )

            await ctx.send(embed=embed)

        else:
            await ctx.send("You have not participated in any trivia.")

    # Display the global trivia leaderboard
    @commands.command()
    @commands.cooldown(1, 30, BucketType.channel)
    async def leaderboard(self, ctx):
        # Scoreboard display embed
        embed = discord.Embed(title="Trivia Leaderboard", colour=discord.Colour(0x44981E))
        embed.set_thumbnail(url=self.bot.user.avatar)

        leader_count = await self.trivia_db.get_leaderboard_count()

        stats = [
            (TriviaLeaderboardType.SCORE, ":trophy: High Scores"),
            (TriviaLeaderboardType.WINS, ":first_place: Wins"),
            (TriviaLeaderboardType.CORRECT_ANSWERS, ":white_check_mark:  Correct Answers"),
            (TriviaLeaderboardType.FASTEST_ANSWER, ":point_up: Fastest Answers"),
            (TriviaLeaderboardType.LONGEST_STREAK, ":four_leaf_clover: Longest Streak"),
        ]
        if leader_count >= 1:
            for stat, category in stats:
                scorers = await self.trivia_db.get_leaderboard_results(stat)

                scores = ""
                for scorer, score in scorers[:5]:
                    scores += f"**{scorer}**: "
                    result = f"{round(score, 2):,}" if isinstance(score, str) else score
                    scores += f"{result}\n"

                embed.add_field(name=category, value=scores, inline=False)

            if len(embed.fields) > 0:
                await ctx.send(embed=embed)

    @app_commands.command(name="start", description="Starts a trivia match with questions from the chosen category.")
    @app_commands.describe(category="The television category to use for the trivia questions.")
    @app_commands.checks.cooldown(1, 120.0, key=lambda i: (i.guild_id, i.user.id))
    async def start_trivia(self, interaction: discord.Interaction, category: Literal["The Simpsons", "Futurama"]):
        if interaction.guild_id is None or interaction.channel is None:
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

        # Load question data from trivia file
        questions = trivia_category.load_questions()

        # Insert new trivia match into DB
        match_id = await self.trivia_db.insert_match(guild_id=interaction.guild_id, category=trivia_category)

        # Continue playing trivia until exit or out of questions
        trivia_match = TriviaMatch(
            host=interaction.user.id, match_id=match_id, category=trivia_category, questions=questions
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
            match = self.matches_in_progress.get(interaction.channel.id)
            if match is None or match.is_finished:
                await interaction.response.send_message("No trivia matches are in progress here.", ephemeral=True)

            elif match.host != interaction.user.id:
                await interaction.response.send_message(
                    "Sorry, you are not the host of this trivia match.", ephemeral=True
                )

            else:
                match.force_end_match()
                await interaction.response.send_message(
                    "The trivia match will end once the current round ends.", ephemeral=True
                )
                self.matches_in_progress.pop(interaction.channel.id)


async def setup(bot):
    await bot.add_cog(Trivia(bot))
