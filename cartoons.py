import aiohttp
import asyncio
import requests

class CartoonAPI:
    def __init__(self, command, url):
        self.command = command
        self.url = url

        self.randomUrl = url + 'api/random'
        self.captionUrl = url + 'caption/{}/{}'
        self.apiCaptionUrl = url + 'api/caption?e={}&t={}'
        self.searchUrl = url + 'api/search?q='
        self.imageUrl = url + 'img/{}/{}.jpg'
        self.gifUrl = url + 'gif/{}/{}/{}'

    async def getRandomCartoon(self, gif=False):
        async with aiohttp.get(self.randomUrl) as cartoonPage:

            if cartoonPage.status == 200:
                cartoonJson = await cartoonPage.json()

                episode = str(cartoonJson['Frame']['Episode'])
                timestamp = cartoonJson['Subtitles'][0]['StartTimestamp']

                caption = ''
                for quote in cartoonJson['Subtitles']:
                    caption += quote['Content'] + '\n'

                if gif:
                    endTimestamp = cartoonJson['Subtitles'][-1]['EndTimestamp']
                    gifLink = self.gifUrl.format(episode, timestamp, endTimestamp)

                    gifLink += '.gif?b64lines='

                    async with aiohttp.get(gifLink) as videoPage:
                        return videoPage.url + '\n' + caption

                else:
                    return self.imageUrl.format(episode, timestamp) + '\n' + caption

    async def findCartoonQuote(self, messageText):

        searchText = messageText[(len(self.command) + 1):].replace(' ', '+')

        search = self.searchUrl + searchText

        async with aiohttp.get(search) as cartoonSearch:

            if cartoonSearch.status == 200:
                searchResults = await cartoonSearch.json()
                if len(searchResults) > 0:
                    firstResult = searchResults[0]

                    episode = str(firstResult['Episode'])
                    timestamp = str(firstResult['Timestamp'])

                    async with aiohttp.get(self.apiCaptionUrl.format(episode, timestamp)) as cartoonCaption:
                        if cartoonCaption.status == 200:
                            captionJson = await cartoonCaption.json()

                            caption = ''
                            for quote in captionJson['Subtitles']:
                                caption += quote['Content'] + '\n'

                            return self.imageUrl.format(episode, timestamp) + '\n' + caption

                        else:
                            return imageUrl + '\n' + 'Error 404. Website may be down.'

                else:
                    return 'No results found.'

            else:
                return 'Error 404. Website may be down.'
