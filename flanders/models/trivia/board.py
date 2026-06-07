from dataclasses import dataclass
from enum import StrEnum


@dataclass
class TriviaScoreboard:
    participant_count: int
    question_count: int
    top_scorers: list[tuple[str, int]]
    highest_accuracy: list[tuple[str, float]]
    fastest_answers: list[tuple[str, int]]


class TriviaLeaderboardType(StrEnum):
    SCORE = "score"
    WINS = "wins"
    CORRECT_ANSWERS = "correct_answers"
    FASTEST_ANSWER = "fastest_answer"
    LONGEST_STREAK = "longest_streak"
