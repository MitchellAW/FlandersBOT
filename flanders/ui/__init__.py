"""All v2 components used by FlandersBOT."""

from flanders.ui.builder_view import BuilderView
from flanders.ui.content_view import TVContentView
from flanders.ui.leaderboard_view import TriviaLeaderboardView
from flanders.ui.privacy_view import TriviaPrivacyView
from flanders.ui.scoreboard_view import TriviaScoreboardView
from flanders.ui.trivia_view import (
    TriviaView,
)
from flanders.ui.user_stats_view import TriviaUserStatsView

__all__ = [
    "BuilderView",
    "TVContentView",
    "TriviaLeaderboardView",
    "TriviaPrivacyView",
    "TriviaScoreboardView",
    "TriviaUserStatsView",
    "TriviaView",
]
