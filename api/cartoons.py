import asyncio
from base64 import b64encode

import aiohttp


class CartoonAPI:
    def __init__(self, url):
        self.url = url
        self.random_url = self.url + 'api/random'
        self.caption_url = self.url + 'api/caption?e={}&t={}'
        self.search_url = self.url + 'api/search?q='
        self.image_url = self.url + 'meme/{}/{}.jpg?b64lines={}'
        self.gif_url = self.url + 'gif/{}/{}/{}.gif?b64lines={}'

    # Generates a random cartoon image/gif, with caption embedded into the
    # image/gif, chooses jpg by default
    async def get_random_cartoon(self, gif=False):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.random_url, timeout=30) as cartoon_page:

                if cartoon_page.status == 200:
                    cartoon_json = await cartoon_page.json()

                    episode = str(cartoon_json['Episode']['Key'])

                    if gif:
                        timestamp = (cartoon_json['Subtitles'][0][
                            'StartTimestamp'])

                        if len(cartoon_json['Subtitles']) < 2:
                            end_timestamp = (cartoon_json['Subtitles'][0][
                                'EndTimestamp'])

                        else:
                            end_timestamp = (cartoon_json['Subtitles'][1][
                                'EndTimestamp'])

                        return self.gif_url.format(episode, timestamp,
                                                   end_timestamp,
                                                   self.encode_caption(
                                                      cartoon_json))

                    else:
                        timestamp = cartoon_json['Frame']['Timestamp']
                        return self.image_url.format(episode, timestamp,
                                                     self.encode_caption(
                                                        cartoon_json))

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

    # Generates a cartoon image/gif, with caption embedded into the image/gif,
    # uses first search result returned from messageText
    async def find_cartoon_quote(self, search_text, gif=False):
        search_text = search_text.replace(' ', '+')
        search = self.search_url + search_text

        async with aiohttp.ClientSession() as session:
            async with session.get(search, timeout=15) as cartoon_search:
                if cartoon_search.status == 200:
                    search_results = await cartoon_search.json()

                    if len(search_results) > 0:
                        first_result = search_results[0]

                        episode = str(first_result['Episode'])
                        timestamp = str(first_result['Timestamp'])

                    else:
                        return 'No search results found.'

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

            async with session.get(self.caption_url.format(episode, timestamp),
                                   timeout=15) as caption:
                if caption.status == 200:
                    cartoon_json = await caption.json()

                    if gif:
                        timestamp = (cartoon_json['Subtitles'][0][
                            'StartTimestamp'])

                        if len(cartoon_json['Subtitles']) < 2:
                            end_timestamp = (cartoon_json['Subtitles'][0][
                                'EndTimestamp'])

                        else:
                            end_timestamp = (cartoon_json['Subtitles'][1][
                                'EndTimestamp'])

                        return self.gif_url.format(episode, timestamp,
                                                   end_timestamp,
                                                   self.encode_caption(
                                                      cartoon_json))

                    else:
                        timestamp = cartoon_json['Frame']['Timestamp']
                        return self.image_url.format(episode, timestamp,
                                                     self.encode_caption(
                                                        cartoon_json))

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

    # Loop through all words of the subtitles, add them to the caption and then
    # return the caption encoded in base64 for use in the url
    def encode_caption(self, caption_json):
        char_count = 0
        line_count = 0
        caption = ''

        for quote in caption_json['Subtitles']:
            for word in quote['Content'].split():
                char_count += len(word) + 1

                if char_count < 24 and line_count < 4:
                    caption += ' %s' % word

                elif line_count < 4:
                    char_count = len(word) + 1
                    line_count += 1
                    if line_count < 4:
                        caption += '\n' + ' %s' % word

        caption = self.shorten_caption(caption)
        encoded = b64encode(str.encode(caption, 'utf-8'), altchars=b'__')

        return encoded.decode('utf-8')

    # Favours ending the caption at the latest sentence ending (., !, ?)
    @staticmethod
    def shorten_caption(caption):
        for i in range(len(caption) - 1, 0, -1):
            if caption[i] == '.' or caption[i] == '!' or caption[i] == '?':
                return caption[:i+1]

        return caption

    # Generate the gif and get the direct url for embedding
    @staticmethod
    async def generate_gif(gif_url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(gif_url, timeout=30) as generator:
                    if generator.status == 200:
                        return generator.url

            except asyncio.TimeoutError:
                return gif_url
