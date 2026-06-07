from dataclasses import dataclass
from enum import StrEnum


@dataclass
class TriviaScoreboardEntry:
    user_id: int
    value: int | float


@dataclass
class TriviaScoreboard:
    participant_count: int
    question_count: int
    top_scorers: list[TriviaScoreboardEntry]
    highest_accuracy: list[TriviaScoreboardEntry]
    fastest_answers: list[TriviaScoreboardEntry]


class TriviaLeaderboardType(StrEnum):
    SCORE = "score"
    WINS = "wins"
    CORRECT_ANSWERS = "correct_answers"
    FASTEST_ANSWER = "fastest_answer"
    LONGEST_STREAK = "longest_streak"
