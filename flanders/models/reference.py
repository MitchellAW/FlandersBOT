from dataclasses import dataclass

import compuglobal

from flanders.bot import FlandersBOT
from flanders.models import UserPreferences


@dataclass
class TVReferenceState:
    bot: FlandersBOT
    api: compuglobal.AsyncCompuGlobalAPI
    api_cache: dict[str, compuglobal.EpisodeSummary]
    user_prefs: UserPreferences
    frames: list[compuglobal.FrameResult]
    channel: int | None = None

    def __post_init__(self) -> None:
        self.custom_subtitles: list[compuglobal.Subtitle] | None = None

        self.frame_key: str = self.frames[0].key
        self.frame_timestamp: int = self.frames[0].timestamp

        # Cache screencaps and subtitles using key + timestamp
        self.screencaps: dict[tuple[str, int], compuglobal.Screencap] = {}
        self.transcripts: dict[tuple[str, int], list[compuglobal.Subtitle]] = {}

    def set_frame(self, key: str, timestamp: int) -> None:
        self.frame_key = key
        self.frame_timestamp = timestamp

    async def cache_screencap(self) -> None:
        screencap = await self.get_screencap()
        if self.channel is not None:
            self.bot.cached_screencaps.update({self.channel: (screencap, self.api.BASE_URL)})

    async def get_screencap(self) -> compuglobal.Screencap:
        screencap = self.screencaps.get((self.frame_key, self.frame_timestamp))

        if screencap is None:
            screencap = await self.api.get_screencap(episode=self.frame_key, timestamp=self.frame_timestamp)
            self.screencaps.update({(screencap.key, screencap.timestamp): screencap})

        return screencap

    async def get_transcript(self) -> list[compuglobal.Subtitle]:
        transcript = self.transcripts.get((self.frame_key, self.frame_timestamp))

        if transcript is None:
            transcript = await self.api.get_transcript(episode=self.frame_key, timestamp=self.frame_timestamp)
            self.transcripts.update({(self.frame_key, self.frame_timestamp): transcript})

        return transcript

    async def get_subtitles(self) -> list[compuglobal.Subtitle]:
        screencap = await self.get_screencap()
        return self.custom_subtitles if self.custom_subtitles is not None else screencap.subtitles

    async def get_comic_strip_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_comic_strip_url(
            screencap,
            subtitles=subtitles,
            overlay_format=self.user_prefs.overlay_preferences,
        )

    async def get_gif_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_gif_url(
            screencap,
            subtitles=subtitles,
            overlay_format=self.user_prefs.overlay_preferences,
        )

    async def get_total_duration(self) -> int:
        subtitles = await self.get_subtitles()
        start_timestamp = min(subtitle.start_timestamp for subtitle in subtitles)
        end_timestamp = max(subtitle.end_timestamp for subtitle in subtitles)
        return end_timestamp - start_timestamp
