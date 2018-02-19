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

    # Post a random moment
    async def post_image(self, ctx, search_text=None, custom_caption=None):
        if search_text is None:
            moment = await self.get_random_moment()

        else:
            moment = await self.search_for_moment(search_text)

        if moment is not None:

            if custom_caption is None:
                await ctx.send(moment.get_image_url())

            else:
                await ctx.send(moment.get_custom_image_url(custom_caption))

    # Post generating message, generate gif then post generated Url
    async def post_gif(self, ctx, search_text=None, custom_caption=None):
        if search_text is None:
            moment = await self.get_random_moment()

        else:
            moment = await self.search_for_moment(search_text)

        if moment is not None:
            if custom_caption is None:
                gif_url = moment.get_gif_url()

            else:
                gif_url = moment.get_custom_gif_url(custom_caption)

            sent = await ctx.send(f'Generating {moment.get_episode()}... '
                                  '<a:loading:410316176510418955>')
            generated_url = await self.generate_gif(gif_url)
            await sent.edit(content=generated_url)

    # Ask user to post a custom caption, take custom caption and generate
    # custom gif, then delete request for caption and post custom gif
    async def post_custom_gif(self, ctx, bot, search_text=None):
        first = await ctx.send('Please post the caption you would like to use',
                               delete_after=30)
        try:
            def check(message):
                return message.author == ctx.message.author

            resp = await bot.wait_for('message', check=check, timeout=30)
            await first.delete()
            await self.post_gif(ctx, search_text, resp.content)

        except asyncio.TimeoutError:
            pass

    # Gets a TV Show moment using episode and timestamp
    async def get_moment(self, episode, timestamp):
        caption_url = self.api_caption_url.format(episode, timestamp)
        async with aiohttp.ClientSession() as session:
            async with session.get(caption_url, timeout=15) as moment:
                if moment.status == 200:
                    moment_json = await moment.json()
                    return Moment(self, moment_json)

    # Gets a random TV Show moment
    async def get_random_moment(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.random_url, timeout=15) as moment_page:

                if moment_page.status == 200:
                    moment_json = await moment_page.json()
                    return Moment(self, moment_json)

    # Searches for a TV Show moment and uses the first search result
    async def search_for_moment(self, search_text):
        search_text = search_text.replace(' ', '+')
        search = self.search_url + search_text

        async with aiohttp.ClientSession() as session:
            async with session.get(search, timeout=15) as moment_search:
                if moment_search.status == 200:
                    search_results = await moment_search.json()

                    if len(search_results) > 0:
                        first_result = search_results[0]
                        episode = first_result['Episode']
                        timestamp = first_result['Timestamp']
                        return await self.get_moment(episode, timestamp)

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
                async with session.get(gif_url, timeout=10) as generator:
                    if generator.status == 200:
                        return generator.url

            except asyncio.TimeoutError:
                return gif_url


class Moment:
    def __init__(self, api, json):
        self.api = api
        self.json = json
        self.episode = self.json['Episode']['Key']
        self.img_url = self.api.url + 'meme/{}/{}.jpg?b64lines={}'
        self.gif_url = self.api.url + 'gif/{}/{}/{}.gif?b64lines={}'

        # Initalise full caption + b64 encoded caption
        self.caption = self.api.json_to_caption(self.json)
        self.b64_caption = self.api.encode_caption(self.caption)

        # Initalise timestamps for image and gif format
        self.frame_timestamp = self.json['Frame']['Timestamp']
        self.start_timestamp = self.json['Subtitles'][0]['StartTimestamp']
        index = min(len(self.json['Subtitles']), 1) - 1
        self.end_timestamp = self.json['Subtitles'][index]['EndTimestamp']

    # Gets the episode for this moment
    def get_episode(self):
        return self.episode

    # Will get the image url for this moment captioned with subtitles
    def get_image_url(self):
        return self.img_url.format(self.episode, self.frame_timestamp,
                                   self.b64_caption)

    # Will get the gif url for this moment captioned with subtitles
    def get_gif_url(self):
        return self.gif_url.format(self.episode, self.start_timestamp,
                                   self.end_timestamp, self.b64_caption)

    # Will get the image url for this moment captioned with a custom caption
    def get_custom_image_url(self, custom_caption):
        return self.img_url.format(self.episode, self.frame_timestamp,
                                   self.api.encode_caption(custom_caption))

    # Will get the gif url for this moment captioned with a custom caption
    def get_custom_gif_url(self, custom_caption):
        return self.gif_url.format(self.episode, self.start_timestamp,
                                   self.end_timestamp,
                                   self.api.encode_caption(custom_caption))
