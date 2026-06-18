from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import compuglobal
from compuglobal import AsyncCompuGlobalAPI, FontColor, OverlayFormat
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from flanders.utils import PreferencesDB


AVAILABLE_COLORS = {
    "White": FontColor.from_hex("ffffff"),
    "Black": FontColor.from_hex("000000"),
    "Gray": FontColor.from_hex("808080"),
    "Red": FontColor.from_hex("ff0000"),
    "Blue": FontColor.from_hex("0000ff"),
    "Yellow": FontColor.from_hex("ffff00"),
    "Green": FontColor.from_hex("008000"),
    "Orange": FontColor.from_hex("ffa500"),
    "Purple": FontColor.from_hex("800080"),
    "Pink": FontColor.from_hex("ffc0cb"),
    "Cyan": FontColor.from_hex("00ffff"),
    "Lime": FontColor.from_hex("00ff00"),
    "Teal": FontColor.from_hex("008080"),
    "Magenta": FontColor.from_hex("ff00ff"),
    "Navy": FontColor.from_hex("000080"),
    "Peach": FontColor.from_hex("ffdab9"),
}


class UserSearchPreferences(BaseModel):
    season_min: int | None = Field(ge=0, default=None)
    season_max: int | None = Field(ge=0, default=None)

    model_config = ConfigDict(
        extra="forbid",
    )


@dataclass
class UserPreferences:
    user_id: int
    tv_show: str
    overlay_preferences: OverlayFormat
    search_preferences: UserSearchPreferences = field(default_factory=UserSearchPreferences)
    advanced_mode: bool = False


@dataclass
class UserPreferenceState:
    api: AsyncCompuGlobalAPI
    cache: dict[str, compuglobal.EpisodeSummary]
    screencap: compuglobal.Screencap
    prefs_db: PreferencesDB
    prefs: UserPreferences

    def __post_init__(self) -> None:
        self.user_id = self.prefs.user_id
        self.tv_show = self.prefs.tv_show
        self.search_prefs = self.prefs.search_preferences
        self.overlay_prefs = self.prefs.overlay_preferences
        self.advanced = self.prefs.advanced_mode

    async def regenerate_image_url(self) -> str:
        return await self.api.get_comic_panel_url(self.screencap, overlay_format=self.overlay_prefs)

    def get_season_range(self) -> tuple[int, int]:
        season_min = min(summary.season for summary in self.cache.values())
        season_max = max(summary.season for summary in self.cache.values())

        return season_min, season_max

    def evenly_spaced_seasons(self, count: int = 10) -> list[int]:
        season_min, season_max = self.get_season_range()
        if count <= 1 or season_max <= season_min:
            return [season_min]

        step = (season_max - season_min) / (count - 1)
        seasons = [round(season_min + i * step) for i in range(count)]

        # Deduplicate seasons
        return sorted(set(seasons))

    async def update_user_preferences(self) -> None:
        preferences = UserPreferences(
            user_id=self.user_id,
            tv_show=self.tv_show,
            search_preferences=self.search_prefs,
            overlay_preferences=self.overlay_prefs,
            advanced_mode=self.advanced,
        )

        await self.prefs_db.update_user_preferences(preferences)

    def restore_defaults(self) -> None:
        self.search_prefs = UserSearchPreferences()
        self.overlay_prefs = self.api.config.default_format.model_copy()
        self.advanced = False
