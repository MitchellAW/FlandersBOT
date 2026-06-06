import json
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

import discord
from pydantic import BaseModel
from pydantic.functional_validators import model_validator

REQUIRED_ANSWERS = 3


class TriviaLeaderboardType(StrEnum):
    SCORE = "score"
    WINS = "wins"
    CORRECT_ANSWERS = "correct_answers"
    FASTEST_ANSWER = "fastest_answer"
    LONGEST_STREAK = "longest_streak"


@dataclass
class TriviaAnswer:
    user_id: int
    username: str
    mention: str
    answer_index: int
    is_correct: bool
    answer_time: int


class TriviaQuestion(BaseModel, frozen=True):
    id: int
    question: str
    answers: tuple[str, str, str]
    source: str
    shuffled_answers: tuple[str, str, str]
    correct_index: int

    @model_validator(mode="before")
    @classmethod
    def derived_fields(cls, data: dict) -> dict:
        answers = data["answers"]
        shuffled = random.sample(answers, len(answers))
        if "shuffled_answers" not in data:
            data["shuffled_answers"] = tuple(shuffled)

        if "correct_index" not in data:
            data["correct_index"] = shuffled.index(answers[0])

        return data

    @property
    def correct_answer(self) -> str:
        return self.answers[0]


@dataclass()
class TriviaCategory:
    category_name: str
    file_name: str
    colour: discord.Colour
    thumbnail_url: str
    end_thumbnail_url: str
    TIMER_DURATION: int = 20

    def load_questions(self) -> list[TriviaQuestion]:
        with Path(f"flanders/cogs/data/{self.file_name}").open() as trivia_data:
            questions = json.load(trivia_data)
            trivia_questions = [TriviaQuestion(id=i, **question) for i, question in enumerate(questions)]
            return random.sample(trivia_questions, len(trivia_questions))


class FuturamaTrivia(TriviaCategory):
    def __init__(self) -> None:
        fry_red = discord.Colour(0x9B2525)
        thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/hypnotoad.gif?raw=true"
        end_thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/hypnotoad-end.png"
        super().__init__("futurama", "futurama_trivia.json", fry_red, thumb, end_thumb)


class SimpsonsTrivia(TriviaCategory):
    def __init__(self) -> None:
        simpsons_yellow = discord.Colour(0xFFEF06)
        thumb = (
            "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/donut.gif?raw=true"
        )
        end_thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/donut-end.png"
        super().__init__("simpsons", "simpsons_trivia.json", simpsons_yellow, thumb, end_thumb)


class RickAndMortyTrivia(TriviaCategory):
    def __init__(self) -> None:
        rick_blue = discord.Colour(0xAAD3EA)
        thumb = (
            "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/portal.gif?raw=true"
        )
        super().__init__("rickandmorty", "ram_trivia.json", rick_blue, thumb, thumb)


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


@dataclass
class TriviaMatch:
    host: int
    match_id: int
    questions: list[TriviaQuestion]
    category: TriviaCategory
    jump_url: str

    _current_round: TriviaRound | None = field(default=None, repr=False)
    _completed_rounds: list[TriviaRound] = field(default_factory=list, repr=False)
    _is_idle: bool = False
    _force_ended: bool = False

    def start_round(self) -> TriviaRound | None:
        if self._current_round is not None:
            msg = "A round is already in progress. Call end_round() first."
            raise RuntimeError(msg)
        if not self.questions:
            msg = "A round is already in progress. Call end_round() first."
            raise RuntimeError(msg)

        question = self.questions.pop()
        self._current_round = TriviaRound(question=question)
        return self._current_round

    def end_round(self) -> TriviaRound:
        if self._current_round is None:
            msg = "No round is currently in progress."
            raise RuntimeError(msg)

        completed = self._current_round
        self._completed_rounds.append(completed)
        completed.end_round()
        self._current_round = None
        return completed

    def end_match_due_to_inactivity(self) -> None:
        self._is_idle = True

    def force_end_match(self) -> None:
        self._force_ended = True

    @property
    def current_round(self) -> TriviaRound | None:
        return self._current_round

    @property
    def completed_rounds(self) -> list[TriviaRound]:
        return list(self._completed_rounds)

    @property
    def is_finished(self) -> bool:
        """True when all questions have been played and no round is open."""
        return self._is_idle or self._force_ended or (not self.questions and self._current_round is None)

    def was_force_ended(self) -> bool:
        return self._force_ended

    def questions_remaining(self) -> int:
        return len(self.questions)

    def rounds_played(self) -> int:
        return len(self._completed_rounds)


@dataclass
class TriviaScoreboard:
    participant_count: int
    question_count: int
    top_scorers: list[tuple[str, int]]
    highest_accuracy: list[tuple[str, float]]
    fastest_answers: list[tuple[str, int]]
