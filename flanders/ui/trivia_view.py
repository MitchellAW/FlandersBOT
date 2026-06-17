from datetime import UTC, datetime, timedelta

import discord

from flanders.models import TriviaMatch, TriviaRound


class TriviaView(discord.ui.LayoutView):
    def __init__(self, trivia_match: TriviaMatch) -> None:
        super().__init__()

        if trivia_match.rounds_played() >= 1:
            answer_container = TriviaAnswerContainer(trivia_match)
            if answer_container is not None:
                self.add_item(answer_container)

        if not trivia_match.is_finished and trivia_match.current_round is not None:
            current_round = trivia_match.current_round
            if current_round is not None:
                question_container = TriviaQuestionContainer(trivia_match, current_round)
                self.add_item(question_container)


class TriviaContainer(discord.ui.Container):
    ANSWER_KEY = ("A", "B", "C")


class TriviaQuestionContainer(TriviaContainer):
    def __init__(
        self,
        trivia_match: TriviaMatch,
        trivia_round: TriviaRound,
    ) -> None:
        super().__init__()

        summary = self.summary(trivia_match, trivia_round)
        summary_text = discord.ui.TextDisplay(content=summary)

        thumb = discord.ui.Thumbnail(media=trivia_match.category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)
        section.add_item(summary_text)

        self.add_item(section)

        row = discord.ui.ActionRow()
        for i, key in enumerate(self.ANSWER_KEY):
            row.add_item(TriviaButton(key=key, index=i, trivia_round=trivia_round))

        self.add_item(row)

        end_time = datetime.now(tz=UTC) + timedelta(seconds=trivia_match.category.TIMER_DURATION)
        time_remaining = discord.utils.format_dt(end_time, style="R")
        content = discord.ui.TextDisplay(content=f"-# Round will end {time_remaining}")
        self.add_item(content)

    def summary(self, trivia_match: TriviaMatch, trivia_round: TriviaRound) -> str:
        current_question = trivia_round.question
        summary = f"### #{trivia_match.rounds_played() + 1}: {current_question.question}\n"
        summary += "".join(
            f"**{key}**: {question}\n"
            for key, question in zip(self.ANSWER_KEY, current_question.shuffled_answers, strict=True)
        )
        summary += "\nSelect your answer below:"
        return summary


class TriviaAnswerContainer(TriviaContainer):
    def __init__(self, trivia_match: TriviaMatch) -> None:
        super().__init__()

        if trivia_match.rounds_played() == 0:
            return

        previous_round = trivia_match.completed_rounds[-1]

        summary = self.summary(trivia_match)

        # Show question and answer content, (with thumbnail alongside) and add it to self
        summary_text = discord.ui.TextDisplay(content=summary)

        thumb = discord.ui.Thumbnail(media=trivia_match.category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)
        section.add_item(summary_text)
        self.add_item(summary_text)

        # Show how long ago previous round ended
        if previous_round.ended_at is not None:
            ended_at = discord.utils.format_dt(previous_round.ended_at, style="R")
            if trivia_match.is_finished:
                scoreboard_time = datetime.now(tz=UTC) + timedelta(
                    seconds=int(trivia_match.category.TIMER_DURATION / 2),
                )
                show_in = discord.utils.format_dt(scoreboard_time, style="R")
                content = discord.ui.TextDisplay(content=f"-# Match ended {ended_at}! Showing results {show_in}...")

            else:
                content = discord.ui.TextDisplay(content=f"-# Round ended {ended_at}")
            self.add_item(content)

    def summary(self, trivia_match: TriviaMatch) -> str:
        previous_round = trivia_match.completed_rounds[-1]
        previous_question = previous_round.question

        summary = (
            f"### #{trivia_match.rounds_played()}: {previous_question.question}\n"
            f"**{self.ANSWER_KEY[previous_question.correct_index]}:** {previous_question.correct_answer}\n"
            f"**Source:** {previous_question.source}"
        )

        answers = previous_round.answers
        correct_answers = previous_round.correct_answers

        if len(answers) == 0:
            summary += "\n\n⛔ **No answers given! Trivia has ended.**"

        elif trivia_match.was_force_ended():
            summary += "\n\n⛔ Trivia was stopped with the `/trivia stop` command."

        elif trivia_match.questions_remaining() == 0:
            summary += "\n\n🎉 All questions have been answered."

        if len(answers) != 0 and len(correct_answers) == 0:
            summary += "\n\n**No correct answers!**"

        else:
            summary += f"\n\n**{len(correct_answers)} correct answers!**\n"
            summary += ", ".join(answer.mention for answer in correct_answers)

        return summary


class TriviaButton(discord.ui.Button):
    def __init__(self, key: str, index: int, trivia_round: TriviaRound) -> None:
        self.view: TriviaView
        self.key = key
        self.index = index
        self.trivia_round = trivia_round

        super().__init__(label=f"{key}", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if not self.trivia_round.is_completed:
            self.trivia_round.log_answer(interaction.user, self.index)
