import compuglobal

from flanders.bot import FlandersBOT


class TVReferenceState:
    def __init__(
        self,
        bot: FlandersBOT,
        api: compuglobal.AsyncCompuGlobalAPI,
        api_cache: dict[str, compuglobal.EpisodeSummary],
        frames: list[compuglobal.FrameResult],
        channel: int | None = None,
    ):
        self.frames = frames
        self.api = api
        self.api_cache = api_cache
        self.channel = channel
        self.bot = bot

        self.custom_subtitles: list[compuglobal.Subtitle] | None = None

        self._index = 0
        self.screencaps: dict[compuglobal.Frame, compuglobal.Screencap] = {}

    def set_index(self, index):
        if index < 0 or index > len(self.frames):
            raise ValueError(f"Index {index} is out of bounds, must be between 0-{len(self.frames)}")

        self._index = index

    async def cache_screencap(self):
        screencap = await self.get_screencap()
        if self.channel is not None:
            self.bot.cached_screencaps.update({self.channel: (screencap, self.api.BASE_URL)})

    async def populate(self):
        for frame in self.frames:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)
            self.screencaps.update({frame: screencap})

    async def get_screencap(self) -> compuglobal.Screencap:
        frame = self.frames[self._index]

        screencap = self.screencaps.get(frame)

        if screencap is None:
            screencap = await self.api.get_screencap(frame.key, frame.timestamp)

        return screencap

    async def get_subtitles(self) -> list[compuglobal.Subtitle]:
        screencap = await self.get_screencap()
        return self.custom_subtitles if self.custom_subtitles is not None else screencap.subtitles

    async def get_comic_strip_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_comic_strip_url(screencap, subtitles=subtitles)

    async def get_gif_url(self) -> str:
        screencap = await self.get_screencap()
        subtitles = await self.get_subtitles()
        return await self.api.get_gif_url(screencap, subtitles=subtitles)

    async def get_total_duration(self) -> int:
        subtitles = await self.get_subtitles()
        start_timestamp = min(subtitle.start_timestamp for subtitle in subtitles)
        end_timestamp = max(subtitle.end_timestamp for subtitle in subtitles)
        return end_timestamp - start_timestamp
