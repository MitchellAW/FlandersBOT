from datetime import datetime, timedelta, timezone

import discord

from flanders.models import TriviaCategory, TriviaMatch, TriviaRound, TriviaScoreboard


class TriviaView(discord.ui.LayoutView):
    def __init__(self, trivia_category: TriviaCategory, trivia_match: TriviaMatch, end_time: datetime):
        self.trivia_category = trivia_category
        self.trivia_match = trivia_match
        self.end_time = end_time
        self.ANSWER_KEY = ["A", "B", "C"]

        super().__init__()

        if trivia_match.rounds_played() >= 1:
            answer_container = self.build_answer_container()
            if answer_container is not None:
                self.add_item(answer_container)

        if not trivia_match.is_finished:
            question_container = self.build_question_container()
            if question_container is not None:
                self.add_item(question_container)

    def build_question_container(self) -> discord.ui.Container | None:
        container = discord.ui.Container()
        trivia_round = self.trivia_match.current_round
        if trivia_round is None:
            return None

        current_question = trivia_round.question

        question_content = f"### #{self.trivia_match.rounds_played() + 1}: {current_question.question}\n"
        answer_content = "".join(
            f"**{key}**: {question}\n"
            for key, question in zip(self.ANSWER_KEY, current_question.shuffled_answers, strict=True)
        )
        answer_content += "\nSelect your answer below:"

        content = f"{question_content}\n{answer_content}\n"
        content = discord.ui.TextDisplay(content=content)

        thumb = discord.ui.Thumbnail(media=self.trivia_category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)
        section.add_item(content)

        container.add_item(section)

        row = discord.ui.ActionRow()
        for i, key in enumerate(self.ANSWER_KEY):
            row.add_item(TriviaButton(key=key, index=i, trivia_round=trivia_round))

        container.add_item(row)

        time_remaining = discord.utils.format_dt(self.end_time, style="R")
        content = discord.ui.TextDisplay(content=f"-# Round will end {time_remaining}")
        container.add_item(content)

        return container

    def build_answer_container(self) -> discord.ui.Container | None:
        container = discord.ui.Container()

        if self.trivia_match.rounds_played() == 0:
            return None

        previous_round = self.trivia_match.completed_rounds[-1]
        previous_question = previous_round.question
        question_content = f"### #{self.trivia_match.rounds_played()}: {previous_question.question}\n"

        answer_content = (
            f"**{self.ANSWER_KEY[previous_question.correct_index]}:** {previous_question.correct_answer}\n"
            f"**Source:** {previous_question.source}"
        )

        answers = previous_round.answers
        correct_answers = previous_round.correct_answers

        if len(answers) == 0:
            answer_content += "\n\n⛔ **No answers given! Trivia has ended.**"

        elif len(answers) == 0 and len(correct_answers) == 0:
            answer_content += "\n\n**No correct answers!**"

        else:
            answer_content += f"\n\n**{str(len(correct_answers))} correct answers!**\n"
            answer_content += ", ".join(answer.mention for answer in correct_answers)

        # Show question and answer content, (with thumbnail alongside) and add it to self
        content = f"{question_content}\n{answer_content}\n"
        content = discord.ui.TextDisplay(content=content)

        thumb = discord.ui.Thumbnail(media=self.trivia_category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)
        section.add_item(content)
        container.add_item(content)

        # Show how long ago previous round ended
        if previous_round.ended_at is not None:
            ended_at = discord.utils.format_dt(previous_round.ended_at, style="R")
            if self.trivia_match.is_finished:
                scoreboard_time = datetime.now(tz=timezone.utc) + timedelta(seconds=10)
                show_in = discord.utils.format_dt(scoreboard_time, style="R")
                content = discord.ui.TextDisplay(content=f"-# Match ended {ended_at}! Showing results {show_in}...")

            else:
                content = discord.ui.TextDisplay(content=f"-# Round ended {ended_at}")
            container.add_item(content)

        return container


class TriviaButton(discord.ui.Button):
    def __init__(self, key: str, index: int, trivia_round: TriviaRound):
        self.view: TriviaView
        self.key = key
        self.index = index
        self.trivia_round = trivia_round

        super().__init__(label=f"{key}", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.trivia_round.is_completed:
            self.trivia_round.log_answer(interaction.user, self.index)


class TriviaScoreboardView(discord.ui.LayoutView):
    def __init__(self, scoreboard: TriviaScoreboard, trivia_category: TriviaCategory):
        super().__init__()

        container = discord.ui.Container()
        thumb = discord.ui.Thumbnail(media=trivia_category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)

        content = "## Trivia Scoreboard"

        participant_count = scoreboard.participant_count

        if participant_count == 0:
            content += "Unfortunately there were no participants in the trivia."

        else:
            top_scorers = scoreboard.top_scorers
            top_scorer, score = top_scorers[0]

            content += f"\nCongratulations to the top scorer, **{top_scorer}**!"

            # List scorers
            scorers = "\n\n### :medal: Correct Answers\n"
            for i, (scorer, score) in enumerate(scoreboard.top_scorers[:5]):
                scorers += f"{i}. **{scorer}**: {round(score, 2):,}\n"

            content += scorers

            # List highest accuracies
            scorers = "\n### :bow_and_arrow: Highest Accuracy\n"
            for i, (scorer, score) in enumerate(scoreboard.highest_accuracy[:5]):
                scorers += f"{i}. **{scorer}**: {round(score * 100.0, 2):,}%\n"
            content += scorers

            # List Fastest Answers
            scorers = "\n### :point_up: Fastest Answers\n"
            for i, (scorer, score) in enumerate(scoreboard.fastest_answers[:5]):
                scorers += f"{i}. **{scorer}**: {round(score / 1000, 3):,}s\n"
            content += scorers

            content += (
                f"\n-# {scoreboard.participant_count} participant{'s' if scoreboard.participant_count > 1 else ''}, "
                f"{scoreboard.question_count} question{'s' if scoreboard.question_count > 1 else ''} answered."
            )

        text_display = discord.ui.TextDisplay(content=content)
        section.add_item(text_display)

        container.add_item(section)
        self.add_item(container)
