"""All v2 components used by FlandersBOT."""

from flanders.components.builder_view import BuilderView
from flanders.components.content_view import TVContentView
from flanders.components.leaderboard_view import TriviaLeaderboardView
from flanders.components.privacy_view import TriviaPrivacyView
from flanders.components.scoreboard_view import TriviaScoreboardView
from flanders.components.trivia_view import (
    TriviaUserStatsView,
    TriviaView,
)

__all__ = [
    "BuilderView",
    "TVContentView",
    "TriviaLeaderboardView",
    "TriviaPrivacyView",
    "TriviaScoreboardView",
    "TriviaUserStatsView",
    "TriviaView",
]
