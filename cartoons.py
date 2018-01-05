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

    def getRandomCartoon(self, gif=False):
        cartoonPage = requests.get(self.randomUrl)
        if cartoonPage.status_code == 200:
            cartoonJson = cartoonPage.json()

            episode = str(cartoonJson['Frame']['Episode'])
            timestamp = cartoonJson['Subtitles'][0]['RepresentativeTimestamp']

            caption = ''
            for quote in cartoonJson['Subtitles']:
                caption += quote['Content'] + '\n'

            if gif:
                endTimestamp = cartoonJson['Subtitles'][-1]['RepresentativeTimestamp']
                videoPage = requests.get(self.gifUrl.format(episode, timestamp, endTimestamp) + '.gif?b64lines=')
                return videoPage.url + '\n' + caption

            else:
                return self.imageUrl.format(episode, timestamp) + '\n' + caption

    def findCartoonQuote(self, messageText):
        searchText = messageText[(len(self.command) + 1):].replace(' ', '+')

        search = self.searchUrl + searchText
        cartoonSearch = requests.get(search)

        if cartoonSearch.status_code == 200:
            searchResults = cartoonSearch.json()
            if len(searchResults) > 0:
                firstResult = searchResults[0]

                episode = str(firstResult['Episode'])
                timestamp = str(firstResult['Timestamp'])

                cartoonCaption = requests.get(self.apiCaptionUrl.format(episode, timestamp))
                if cartoonCaption.status_code == 200:
                    caption = ''
                    for quote in cartoonCaption.json()['Subtitles']:
                        caption += quote['Content'] + '\n'

                    return self.imageUrl.format(episode, timestamp) + '\n' + caption

                else:
                    return imageUrl + '\n' + 'Error 404. Website may be down.'

            else:
                return 'No results found.'

        else:
            return 'Error 404. Website may be down.'

