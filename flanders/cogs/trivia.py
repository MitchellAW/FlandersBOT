import asyncio
import time

import discord
from discord.ext import commands
from discord.ext.commands import BucketType, Context

from flanders.models import FuturamaTrivia, SimpsonsTrivia, TriviaCategory, TriviaMatch, TriviaQuestion, TriviaRound
from flanders.utils import TriviaDB
from flanders.utils.trivia_db import TriviaLeaderboardType

TRIVIA_ROLE = "Trivia Moderator"


# If guild has trivia mod role, require users to have role to start matches, otherwise anyone can start matches
def has_trivia_permissions():
    def predicate(ctx):
        # Get custom trivia role from guild and user
        guild_role = discord.utils.get(ctx.guild.roles, name=TRIVIA_ROLE)
        user_role = discord.utils.get(ctx.author.roles, name=TRIVIA_ROLE)

        # Get manage messages permission from user
        manage_messages_perm = ctx.author.guild_permissions.manage_messages

        # If guild doesn't have trivia role, then stop command requires manage messages permissions
        if guild_role is None and ctx.command.qualified_name == "forcestop":
            return manage_messages_perm

        # If guild doesn't have trivia role, then trivia can be started by anyone
        elif guild_role is None:
            return True

        # If guild has role, trivia role is required to start/stop trivia matches
        else:
            return user_role is not None

    return commands.check(predicate)


class Trivia(commands.Cog):
    DISABLED = True
    DISABLED_MESSAGE = "Sorry, trivia is currently under maintenance at the moment!"

    def __init__(self, bot):
        self.bot = bot
        self.TIMER_DURATION = 16
        self.channels_playing = []
        self.answer_key = {"🇦": 0, "🇧": 1, "🇨": 2}
        self.trivia_db = TriviaDB(db=self.bot.db)

    async def sorry_message(self, ctx):
        await ctx.send(self.DISABLED_MESSAGE, silent=True, delete_after=10)

    # Starts a game of trivia using the simpsons trivia questions
    @commands.command(aliases=["strivia", "simpsontrivia"])
    @commands.cooldown(10, 300, BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @has_trivia_permissions()
    async def simpsonstrivia(self, ctx: Context):
        if self.DISABLED:
            await self.sorry_message(ctx)
            return

        if ctx.channel.id not in self.channels_playing:
            await self.start_trivia(ctx, SimpsonsTrivia())

    # Starts a game of trivia using the futurama trivia questions
    @commands.command(aliases=["ftrivia"])
    @commands.cooldown(10, 300, BucketType.channel)
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    @has_trivia_permissions()
    async def futuramatrivia(self, ctx):
        if self.DISABLED:
            await self.sorry_message(ctx)
            return

        if ctx.channel.id not in self.channels_playing:
            await self.start_trivia(ctx, FuturamaTrivia())

    # TODO: Starts a game of trivia using rick and morty trivia questions
    @commands.command(aliases=["ramtrivia"])
    @commands.cooldown(10, 300, BucketType.channel)
    @has_trivia_permissions()
    async def rickandmortytrivia(self, ctx):
        await ctx.send("Coming Soon!", silent=True, delete_after=10)

    # Explain how trivia games end  to users trying to use a stop command
    @commands.command()
    @commands.cooldown(1, 3, BucketType.channel)
    async def stop(self, ctx):
        if ctx.channel.id in self.channels_playing:
            await ctx.send(
                "The game of trivia will end once nobody answers a question or a member with manage server permissions "
                "uses the forcestop command."
            )

    # Allow users with manage server permissions to force stop trivia games
    @commands.command()
    @has_trivia_permissions()
    async def forcestop(self, ctx):
        if ctx.channel.id in self.channels_playing:
            self.channels_playing.remove(ctx.channel.id)
            await ctx.send("Trivia will terminate at the end of the current round.")

    # Show the scoreboard for the latest match this guild has completed
    @commands.command()
    @commands.cooldown(1, 60, BucketType.channel)
    @has_trivia_permissions()
    async def scoreboard(self, ctx):
        if self.DISABLED:
            await self.sorry_message(ctx)
            return

        # Check if guild has participated
        if result := await self.trivia_db.get_latest_match_details(ctx.guild.id):
            # Get latest match for guild
            match_id, category = result

            category = SimpsonsTrivia()
            if category == "futurama":
                category = FuturamaTrivia()

            # Show scoreboard
            await self.show_scoreboard(ctx, match_id, category)

        else:
            await ctx.send("No previous match found.")

    # Display a users trivia stats
    @commands.command(aliases=["mystatistics", "mystat", "triviastat", "triviastats", "triviastatistics"])
    @commands.cooldown(1, 30, BucketType.user)
    async def mystats(self, ctx):
        if self.DISABLED:
            await self.sorry_message(ctx)
            return
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
        if self.DISABLED:
            await self.sorry_message(ctx)

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

    # Starts a match of trivia (multiple rounds of questions)
    async def start_trivia(self, ctx, category: TriviaCategory):
        if self.DISABLED:
            await self.sorry_message(ctx)
            return

        self.channels_playing.append(ctx.channel.id)

        # Load question data from trivia file
        questions = category.load_questions()

        # Insert new trivia match into DB
        match_id = await self.trivia_db.insert_match(guild_id=ctx.guild.id, category=category)

        # Continue playing trivia until exit or out of questions
        trivia_session = TriviaMatch(match_id=match_id, category=category, questions=questions)

        while ctx.channel.id in self.channels_playing and trivia_session.questions_remaining() > 0:
            await self.play_round(ctx, trivia_session)

        # Set the match as complete (Triggers leaderboard stat updates)
        await self.trivia_db.complete_match(match_id=match_id)

        await self.show_scoreboard(ctx, match_id, category)

    # Starts a round of trivia (single question)
    async def play_round(self, ctx, trivia_session: TriviaMatch):
        trivia_round = trivia_session.start_round()
        if trivia_round is None:
            return

        trivia_question = trivia_round.question
        if trivia_question is None:
            return

        answers = trivia_question.shuffled_answers

        correct_index = answers.index(trivia_question.correct_answer)
        correct_choice = chr(correct_index + 65)

        # Insert new trivia round into DB
        round_id = await self.trivia_db.insert_round(
            match_id=trivia_session.match_id, question_index=trivia_question.id
        )

        # Send the trivia question
        embed = await self.build_question_embed(
            trivia_session=trivia_session, trivia_question=trivia_question, answers=answers
        )
        question = await ctx.send(embed=embed, delete_after=self.TIMER_DURATION + 3)

        await self.gather_answers(ctx, question, trivia_round)

        trivia_session.end_round()

        answers = trivia_round.answers
        for answer in answers:
            await self.trivia_db.insert_answer(round_id, answer)

        # Set round as complete (Triggers leaderboard stat updates)
        await self.trivia_db.complete_round(round_id)

        # Check the results of the trivia question
        # embed.set_thumbnail(url="")
        embed.description = (
            f"**{correct_choice}:** {trivia_question.correct_answer}\n**Source:** <{trivia_question.source}> \n\n"
        )

        answer_count = trivia_round.total_answers
        correct_answers = trivia_round.correct_answers

        # Give statement about result based on # of correct answers recorded
        if answer_count == 0:
            embed.description += "⛔ **No answers given! Trivia has ended.**"
            if ctx.channel.id in self.channels_playing:
                self.channels_playing.remove(ctx.channel.id)

        elif answer_count > 0 and len(correct_answers) == 0:
            embed.description += "**No correct answers!**"

        elif answer_count == 1 and len(correct_answers) == 1:
            embed.description += "**Correct!**"

        else:
            embed.description += f"**{str(len(correct_answers))} correct answers!**"
            for answer in correct_answers:
                embed.description += f"\n{answer.username}"

        await ctx.send(embed=embed, delete_after=self.TIMER_DURATION + 3)

    async def gather_answers(
        self,
        ctx: Context,
        question: discord.Message,
        trivia_round: TriviaRound,
    ) -> None:

        # Add the answer react boxes
        answer_reactions = ["🇦", "🇧", "🇨"]
        try:
            for reaction in answer_reactions:
                await question.add_reaction(reaction)

        # Reaction permission removed after starting trivia
        except discord.errors.Forbidden:
            await question.delete()
            await ctx.send(
                "⛔ Sorry, I do not have the permissions riddly-required to continue!\nRequires: Add Reactions"
            )
            self.channels_playing.remove(ctx.channel.id)

        # Check for confirming a valid answer was made (A, B or C)
        def is_answer(reaction, user):
            return not user.bot and str(reaction.emoji) in ["🇦", "🇧", "🇨"] and reaction.message.channel == ctx.channel

        # Start timer
        end_time = time.time() + self.TIMER_DURATION

        try:
            # Wait until timer ends for each question before displaying results
            while time.time() < end_time:
                react, user = await self.bot.wait_for("reaction_add", check=is_answer, timeout=end_time - time.time())
                answer_index = self.answer_key[str(react.emoji)]
                trivia_round.log_answer(user_id=user.id, username=user.name, answer_index=answer_index)

        except asyncio.TimeoutError:
            pass

    async def build_question_embed(
        self, trivia_session: TriviaMatch, trivia_question: TriviaQuestion, answers: tuple[str, str, str]
    ) -> discord.Embed:
        answer_msg = f"**A:** {answers[0]} \n**B:** {answers[1]} \n**C:** {answers[2]} \n\nReact below to answer!"

        embed = discord.Embed(
            title=f"#{trivia_session.rounds_played() + 1}: {trivia_question.question}",
            colour=trivia_session.category.colour,
            description=answer_msg,
        )
        embed.set_thumbnail(url=trivia_session.category.thumbnail_url)

        return embed

    # Show an embed scoreboard for the given match_id
    async def show_scoreboard(self, ctx, match_id, category):
        scoreboard = await self.trivia_db.get_scoreboard(match_id)

        # Check if match occurred
        if scoreboard is None:
            return None

        # Check if there were anyone competing in the match
        if len(scoreboard.top_scorers) == 0:
            return

        # Get top scorer
        top_scorer, top_score = scoreboard.top_scorers[0]

        # Scoreboard display embed
        embed = discord.Embed(
            title="Trivia Scoreboard",
            description=f"Congratulations to the top scorer, **{top_scorer}**! :trophy:\n",
            color=category.colour,
        )

        # List scorers
        scorers = ""
        for scorer, score in scoreboard.top_scorers[:5]:
            scorers += f"**{scorer}**: {round(score, 2):,}\n"
        embed.add_field(name="\u200b\n*:medal:Correct Answers*", value=scorers)

        # List highest accuracies
        scorers = ""
        for scorer, score in scoreboard.highest_accuracy[:5]:
            scorers += f"**{scorer}**: {round(score * 100.0, 2):,}%\n"
        embed.add_field(name="\u200b\n*:bow_and_arrow: Highest Accuracy*", value=scorers)

        # List Fastest Answers
        scorers = "" if len(scoreboard.fastest_answers) > 0 else "---"
        for scorer, score in scoreboard.fastest_answers[:5]:
            scorers += f"**{scorer}**: {round(score / 1000, 3):,}s\n"
        embed.add_field(name="\u200b\n*:point_up: Fastest Answers*", value=scorers)

        embed.set_footer(
            text=f"{scoreboard.participant_count} participant{'s' if scoreboard.participant_count > 1 else ''}, "
            f"{scoreboard.question_count} question{'s' if scoreboard.question_count > 1 else ''} answered."
        )

        # Display the scoreboard
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Trivia(bot))
