"""All models used by FlandersBOT."""

from flanders.models.preferences import AVAILABLE_COLORS, UserPreferences, UserPreferenceState, UserSearchPreferences
from flanders.models.reference import TVReferenceState
from flanders.models.trivia.board import (
    TriviaLeaderboardEntry,
    TriviaLeaderboardType,
    TriviaScoreboard,
    TriviaScoreboardEntry,
)
from flanders.models.trivia.category import FuturamaTrivia, RickAndMortyTrivia, SimpsonsTrivia, TriviaCategory
from flanders.models.trivia.match import TriviaMatch
from flanders.models.trivia.question import TriviaAnswer, TriviaQuestion
from flanders.models.trivia.round import TriviaRound
from flanders.models.trivia.user_stats import TriviaUserStat, TriviaUserStats

__all__ = [
    "AVAILABLE_COLORS",
    "FuturamaTrivia",
    "RickAndMortyTrivia",
    "SimpsonsTrivia",
    "TVReferenceState",
    "TriviaAnswer",
    "TriviaCategory",
    "TriviaLeaderboardEntry",
    "TriviaLeaderboardType",
    "TriviaMatch",
    "TriviaQuestion",
    "TriviaRound",
    "TriviaScoreboard",
    "TriviaScoreboardEntry",
    "TriviaUserStat",
    "TriviaUserStats",
    "UserPreferenceState",
    "UserPreferences",
    "UserSearchPreferences",
]
