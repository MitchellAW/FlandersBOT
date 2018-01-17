import aiohttp

from base64 import b64encode

class CartoonAPI:
    def __init__(self, command, url):
        self.url = url
        self.command = command
        self.randomUrl = self.url + 'api/random'
        self.captionUrl = self.url + 'api/caption?e={}&t={}'
        self.searchUrl = self.url + 'api/search?q='
        self.imageUrl = self.url + 'meme/{}/{}.jpg?b64lines={}'
        self.gifUrl = self.url + 'gif/{}/{}/{}.gif?b64lines={}'

    # Generates a random cartoon image/gif, with caption embedded into the
    # image/gif, chooses jpg by default
    async def getRandomCartoon(self, gif=False):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.randomUrl) as cartoonPage:

                if cartoonPage.status == 200:
                    cartoonJson = await cartoonPage.json()

                    episode = str(cartoonJson['Episode']['Key'])

                    if gif:
                        timestamp = cartoonJson['Subtitles'][0]['StartTimestamp']

                        if len(cartoonJson['Subtitles']) < 2:
                            endTimestamp = cartoonJson['Subtitles'][0]['EndTimestamp']

                        else:
                            endTimestamp = cartoonJson['Subtitles'][1]['EndTimestamp']

                        return self.gifUrl.format(episode, timestamp, endTimestamp, self.encodeCaption(cartoonJson))

                    else:
                        timestamp = cartoonJson['Frame']['Timestamp']
                        return self.imageUrl.format(episode, timestamp, self.encodeCaption(cartoonJson))

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

    # Generates a cartoon image/gif, with caption embedded into the image/gif,
    # uses first search result returned from messageText
    async def findCartoonQuote(self, messageText, gif=False):
        searchText = messageText[(len(self.command) + 1):].replace(' ', '+')

        search = self.searchUrl + searchText

        async with aiohttp.ClientSession() as session:
            async with session.get(search) as cartoonSearch:
                if cartoonSearch.status == 200:
                    searchResults = await cartoonSearch.json()

                    if len(searchResults) > 0:
                        firstResult = searchResults[0]

                        episode = str(firstResult['Episode'])
                        timestamp = str(firstResult['Timestamp'])

                        async with session.get(self.captionUrl.format(episode, timestamp)) as caption:
                            if caption.status == 200:
                                cartoonJson = await caption.json()

                                if gif:
                                    timestamp = cartoonJson['Subtitles'][0]['StartTimestamp']

                                    if len(cartoonJson['Subtitles']) < 2:
                                        endTimestamp = cartoonJson['Subtitles'][0]['EndTimestamp']

                                    else:
                                        endTimestamp = cartoonJson['Subtitles'][1]['EndTimestamp']

                                    return self.gifUrl.format(episode, timestamp, endTimestamp, self.encodeCaption(cartoonJson))

                                else:
                                    timestamp = cartoonJson['Frame']['Timestamp']
                                    return self.imageUrl.format(episode, timestamp, self.encodeCaption(cartoonJson))

                    else:
                        return 'No search results found.'

                else:
                    return 'Error 404. {} may be down.'.format(self.url)

    # Loop through all words of the subtitles, add them to the caption and then
    # return the caption encoded in base64 for use in the url
    def encodeCaption(self, captionJson):
        charCount = 0
        lineCount = 0
        caption = ''

        for quote in captionJson['Subtitles']:
            for word in quote['Content'].split():
                charCount += len(word) + 1

                # Only allow 4 lines of captions to avoid covering the gif
                if lineCount < 4:
                    caption += ' ' + word

                    # Favour ending captions at ends of sentences
                    if '.' in word or '!' in word or '?' in word:
                        return str(b64encode(str.encode(caption)), 'utf-8')

                    if charCount > 20:
                        charCount = 0
                        lineCount += 1
                        caption += '\n'

        return str(b64encode(str.encode(caption)), 'utf-8')
