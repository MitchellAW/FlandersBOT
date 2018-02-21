import asyncio
from base64 import b64encode

import aiohttp


# TODO: Re-implement error messages
class TVShowAPI:
    def __init__(self, url):
        self.url = url
        self.random_url = self.url + 'api/random'
        self.api_caption_url = self.url + 'api/caption?e={}&t={}'
        self.search_url = self.url + 'api/search?q='
        self.frames_url = self.url + 'api/frames/{}/{}/{}/{}'

    # Gets a TV Show moment using episode and timestamp
    async def get_moment(self, episode, timestamp):
        caption_url = self.api_caption_url.format(episode, timestamp)
        async with aiohttp.ClientSession() as session:
            async with session.get(caption_url, timeout=15) as moment_page:
                if moment_page.status == 200:
                    return Moment(self, await moment_page.json())

    # Gets a random TV Show moment
    async def get_random_moment(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.random_url, timeout=15) as moment_page:

                if moment_page.status == 200:
                    return Moment(self, await moment_page.json())

    # Searches for a TV Show moment and uses the first search result
    async def search_for_moment(self, search_text):
        search = self.search_url + search_text.replace(' ', '+')

        async with aiohttp.ClientSession() as session:
            async with session.get(search, timeout=15) as moment_page:
                if moment_page.status == 200:
                    search_results = await moment_page.json()

                    if len(search_results) > 0:
                        first_result = search_results[0]
                        return await self.get_moment(first_result['Episode'],
                                                     first_result['Timestamp'])

    # Will get all valid frames before and after timestamp for the episode
    async def get_frames(self, episode, timestamp, before, after):
        frames_url = self.frames_url.format(episode, timestamp, before, after)
        async with aiohttp.ClientSession() as session:
            async with session.get(frames_url, timeout=15) as frames_page:
                if frames_page.status == 200:
                    return await frames_page.json()

    # Loop through all words of the subtitles, add them to the caption and then
    # return the caption encoded in base64 for use in the url
    def encode_caption(self, caption):
        char_count = 0
        line_count = 0
        formatted_caption = ''

        for word in caption.split():
            char_count += len(word) + 1

            if char_count < 24 and line_count < 4:
                formatted_caption += ' %s' % word

            elif line_count < 4:
                char_count = len(word) + 1
                line_count += 1
                if line_count < 4:
                    formatted_caption += '\n' + ' %s' % word

        caption = self.shorten_caption(formatted_caption)
        encoded = b64encode(str.encode(caption, 'utf-8'), altchars=b'__')

        return encoded.decode('utf-8')

    # Favours ending the caption at the latest sentence ending (., !, ?)
    @staticmethod
    def shorten_caption(caption):
        for i in range(len(caption) - 1, 0, -1):
            if caption[i] == '.' or caption[i] == '!' or caption[i] == '?':
                return caption[:i + 1]

        return caption

    # Take caption json file and convert it to the caption for encoding
    @staticmethod
    def json_to_caption(cartoon_json):
        caption = ''
        for quote in cartoon_json['Subtitles']:
            caption += quote['Content'] + ' '

        return caption

    # Generate the gif and get the direct url for embedding
    @staticmethod
    async def generate_gif(gif_url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(gif_url, timeout=15) as generator:
                    if generator.status == 200:
                        return generator.url

            # If gif fails to generate before timeout, return original url
            except asyncio.TimeoutError:
                return gif_url


class Moment:
    def __init__(self, api: TVShowAPI, json):
        self.api = api
        self.json = json
        self.episode = self.json['Episode']['Key']
        self.title = self.json['Episode']['Title']
        self.img_url = self.api.url + 'meme/{}/{}.jpg?b64lines={}'
        self.gif_url = self.api.url + 'gif/{}/{}/{}.gif?b64lines={}'

        # Initalise full caption + b64 encoded caption
        self.caption = self.api.json_to_caption(self.json)

        # Initalise timestamp of episode
        self.timestamp = self.json['Frame']['Timestamp']

    # Gets the episode for the moment
    def get_episode(self):
        return self.episode

    # Gets the title of the episode for the moment
    def get_title(self):
        return self.title

    # Gets the timestamp of the frame for the moment
    def get_timestamp(self):
        return self.timestamp

    # Gets the API used to generate the moment
    def get_api(self):
        return self.api

    # Gets the image url for the moment captioned with subtitles
    def get_image_url(self, caption=None):
        if caption is None:
            caption = self.caption

        return self.img_url.format(self.episode, self.timestamp,
                                   self.api.encode_caption(caption))

    # Gets the gif url for the moment captioned with subtitles, defaults gif
    # length to < ~7500ms, before + after must not exceed 10,000ms (10 sec.)
    async def get_gif_url(self, caption=None, before=3500, after=3500):
        if caption is None:
            caption = self.caption

        # Get start and end frame numbers for gif
        frames = await self.api.get_frames(self.episode, self.timestamp,
                                           int(before), int(after))
        start = frames[0]['Timestamp']
        end = frames[-1]['Timestamp']
        return self.gif_url.format(self.episode, start, end,
                                   self.api.encode_caption(caption))
