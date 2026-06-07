from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum


@dataclass
class TriviaScoreboardEntry:
    user_id: int
    value: int | float


@dataclass
class TriviaScoreboard:
    participant_count: int = 0
    question_count: int = 0
    top_scorers: list[TriviaScoreboardEntry] = field(default_factory=list)
    highest_accuracy: list[TriviaScoreboardEntry] = field(default_factory=list)
    fastest_answers: list[TriviaScoreboardEntry] = field(default_factory=list)

    def __str__(self) -> str:
        def plural(count: int, word: str) -> str:
            return f"{count} {word}{'s' if count != 1 else ''}"

        def format_entries(entries: list[TriviaScoreboardEntry], fmt: Callable) -> str:
            if len(entries) == 0:
                return "-----\n"
            return "\n".join(
                f"{i}. <@!{entry.user_id}>: {fmt(entry.value)}" for i, entry in enumerate(entries[:5], start=1)
            )

        if self.participant_count == 0:
            return "## Trivia Scoreboard\n\nUnfortunately, there were no participants in the trivia."

        sections = [
            "## Trivia Scoreboard",
            f"🏆 Congratulations to the top scorer, **<@!{self.top_scorers[0].user_id}>**!",
            f"### 🏅 Correct Answers\n{format_entries(self.top_scorers, lambda v: f'{round(v, 2):,}')}",
            f"### 🏹 Highest Accuracy\n{format_entries(self.highest_accuracy, lambda v: f'{round(v * 100.0, 2):,}%')}",
            f"### ☝️ Fastest Answers\n{format_entries(self.fastest_answers, lambda v: f'{round(v / 1000, 3):,}s')}",
            f"-# {plural(self.participant_count, 'participant')}, {plural(self.question_count, 'question')} answered.",
        ]
        return "\n\n".join(sections)


class TriviaLeaderboardType(StrEnum):
    SCORE = "score"
    WINS = "wins"
    CORRECT_ANSWERS = "correct_answers"
    FASTEST_ANSWER = "fastest_answer"
    LONGEST_STREAK = "longest_streak"


@dataclass
class TriviaLeaderboardEntry:
    username: str
    value: int | float
