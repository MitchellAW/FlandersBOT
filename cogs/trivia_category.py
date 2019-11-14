import discord


class TriviaCategory:
    def __init__(self, category_name, file_name, colour,
                 thumbnail_url, end_thumbnail_url):

        self.category_name = category_name
        self.file_name = file_name
        self.colour = colour
        self.thumbnail_url = thumbnail_url
        self.end_thumbnail_url = end_thumbnail_url


class FuturamaTrivia(TriviaCategory):
    def __init__(self):
        fry_red = discord.Colour(0x9b2525)

        thumb = ('https://raw.githubusercontent.com/MitchellAW/MitchellAW.'
                 'github.io/master/images/hypnotoad-timer.gif')

        end_thumb = ('https://raw.githubusercontent.com/MitchellAW/MitchellAW.'
                     'github.io/master/images/hypnotoad-end.png')

        super().__init__('futurama', 'futurama_trivia.json', fry_red,
                         thumb, end_thumb)


class SimpsonsTrivia(TriviaCategory):
    def __init__(self):
        simpsons_yellow = discord.Colour(0xffef06)

        thumbnail = ('https://raw.githubusercontent.com/MitchellAW/MitchellAW.g'
                     'ithub.io/master/images/donut-timer.gif')

        end_thumbnail = ('https://raw.githubusercontent.com/MitchellAW/Mitchell'
                         'AW.github.io/master/images/donut-end.png')

        super().__init__('simpsons', 'simpsons_trivia.json',
                         simpsons_yellow, thumbnail, end_thumbnail)


class RickAndMortyTrivia(TriviaCategory):
    def __init__(self):
        rick_blue = discord.Colour(0xaad3ea)
        thumbnail = ('https://github.com/MitchellAW/MitchellAW.github.io/blob/m'
                     'aster/images/rick-morty-portal.gif?raw=true')

        super().__init__('rickandmorty', 'ram_trivia.json',
                         rick_blue, thumbnail, thumbnail)
