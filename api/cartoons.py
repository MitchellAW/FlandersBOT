import asyncio
from base64 import b64encode

import aiohttp


class CartoonAPI:
    def __init__(self, url):
        self.url = url
        self.random_url = self.url + 'api/random'
        self.caption_url = self.url + 'api/caption?e={}&t={}'
        self.search_url = self.url + 'api/search?q='
        self.img_url = self.url + 'meme/{}/{}.jpg?b64lines={}'
        self.gif_url = self.url + 'gif/{}/{}/{}.gif?b64lines={}'

    # Post a random moment
    async def post_image(self, ctx, search_terms=None):
        if search_terms is None:
            await ctx.send(await self.get_random_cartoon())

        else:
            await ctx.send(await self.search_cartoon(search_terms, False))

    # Post generating message, generate gif then post generated Url
    async def post_gif(self, ctx, search_terms=None):
        if search_terms is None:
            gif_url = await self.get_random_cartoon(True)

        else:
            gif_url = await self.search_cartoon(search_terms, True)

        if 'https://' not in gif_url:
            await ctx.send(gif_url)

        else:
            sent = await ctx.send('Generating... '
                                  '<a:loading:410316176510418955>')
            generated_url = await self.generate_gif(gif_url)
            await sent.edit(content=generated_url)

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

                        caption = self.json_to_caption(cartoon_json)
                        return self.gif_url.format(episode, timestamp,
                                                   end_timestamp,
                                                   self.encode_caption(caption))

                    else:
                        timestamp = cartoon_json['Frame']['Timestamp']
                        caption = self.json_to_caption(cartoon_json)
                        return self.img_url.format(episode, timestamp,
                                                   self.encode_caption(caption))

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

    # Generates a cartoon image/gif, with caption embedded into the image/gif,
    # uses first search result returned from messageText
    async def search_cartoon(self, search_text, gif=False):
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

                        caption = self.json_to_caption(cartoon_json)
                        return self.gif_url.format(episode, timestamp,
                                                   end_timestamp,
                                                   self.encode_caption(caption))

                    else:
                        timestamp = cartoon_json['Frame']['Timestamp']
                        caption = self.json_to_caption(cartoon_json)
                        return self.img_url.format(episode, timestamp,
                                                   self.encode_caption(caption))

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

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

    # Take caption json file and convert it to the caption for encoding
    @staticmethod
    def json_to_caption(cartoon_json):
        caption = ''
        for quote in cartoon_json['Subtitles']:
            caption += quote['Content'] + ' '

        return caption

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
                async with session.get(gif_url, timeout=10) as generator:
                    if generator.status == 200:
                        return generator.url

            except asyncio.TimeoutError:
                return gif_url
