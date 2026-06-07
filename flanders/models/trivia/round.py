from dataclasses import dataclass, field
from datetime import UTC, datetime

import discord

from flanders.models.trivia.question import TriviaAnswer, TriviaQuestion


@dataclass
class TriviaRound:
    question: TriviaQuestion
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _answers: dict[int, TriviaAnswer] = field(default_factory=dict, repr=False)
    ended_at: datetime | None = None

    @property
    def elapsed_milliseconds(self) -> int:
        return int((datetime.now(UTC) - self.started_at).total_seconds() * 1000)

    def log_answer(self, user: discord.User | discord.Member, answer_index: int) -> None:
        is_correct = answer_index == self.question.correct_index
        answer = TriviaAnswer(
            user_id=user.id,
            username=user.name,
            mention=user.mention,
            answer_index=answer_index,
            is_correct=is_correct,
            answer_time=self.elapsed_milliseconds,
        )
        self._answers[user.id] = answer

    def end_round(self) -> None:
        self.ended_at = datetime.now(UTC)

    @property
    def is_completed(self) -> bool:
        return self.ended_at is not None

    @property
    def answers(self) -> list[TriviaAnswer]:
        return list(self._answers.values())

    @property
    def correct_answers(self) -> list[TriviaAnswer]:
        return [answer for answer in self._answers.values() if answer.is_correct]

    @property
    def incorrect_answers(self) -> list[TriviaAnswer]:
        return [answer for answer in self._answers.values() if not answer.is_correct]

    @property
    def total_answers(self) -> int:
        return len(self._answers)
