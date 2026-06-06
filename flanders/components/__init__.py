"""All v2 components used by FlandersBOT."""

from flanders.components.builder_view import BuilderView
from flanders.components.caption_button import CustomiseCaptionButton, ToggleTimingButton
from flanders.components.content_view import TVContentView
from flanders.components.generate_button import GenerateButton, GenerateComicButton, GenerateGifButton
from flanders.components.search_dropdown import SearchResult, SearchResultDropdown
from flanders.components.trivia_view import (
    TriviaLeaderboardView,
    TriviaPrivacyView,
    TriviaScoreboardView,
    TriviaUserStatsView,
    TriviaView,
)

__all__ = [
    "BuilderView",
    "CustomiseCaptionButton",
    "GenerateButton",
    "GenerateComicButton",
    "GenerateGifButton",
    "SearchResult",
    "SearchResultDropdown",
    "TVContentView",
    "ToggleTimingButton",
    "TriviaLeaderboardView",
    "TriviaPrivacyView",
    "TriviaScoreboardView",
    "TriviaUserStatsView",
    "TriviaView",
]
