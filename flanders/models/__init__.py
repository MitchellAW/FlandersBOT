"""All models used by FlandersBOT."""

from flanders.models.reference import TVReferenceState
from flanders.models.trivia.board import TriviaLeaderboardType, TriviaScoreboard
from flanders.models.trivia.category import FuturamaTrivia, RickAndMortyTrivia, SimpsonsTrivia, TriviaCategory
from flanders.models.trivia.match import TriviaMatch
from flanders.models.trivia.question import TriviaAnswer, TriviaQuestion
from flanders.models.trivia.round import TriviaRound

__all__ = [
    "FuturamaTrivia",
    "RickAndMortyTrivia",
    "SimpsonsTrivia",
    "TVReferenceState",
    "TriviaAnswer",
    "TriviaCategory",
    "TriviaLeaderboardType",
    "TriviaMatch",
    "TriviaQuestion",
    "TriviaRound",
    "TriviaScoreboard",
]
