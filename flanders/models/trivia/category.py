import json
import random
from dataclasses import dataclass

import anyio
import discord

from flanders.models.trivia.question import TriviaQuestion


@dataclass()
class TriviaCategory:
    category_name: str
    file_name: str
    colour: discord.Colour
    thumbnail_url: str
    end_thumbnail_url: str
    TIMER_DURATION: int = 20

    async def load_questions(self) -> list[TriviaQuestion]:
        async with await anyio.open_file(f"flanders/cogs/data/{self.file_name}") as trivia_file:
            trivia_data = await trivia_file.read()
            questions = json.loads(trivia_data)
            trivia_questions = [TriviaQuestion(id=i, **question) for i, question in enumerate(questions)]
            return random.sample(trivia_questions, len(trivia_questions))


class FuturamaTrivia(TriviaCategory):
    def __init__(self) -> None:
        fry_red = discord.Colour(0x9B2525)
        thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/hypnotoad.gif?raw=true"
        end_thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/hypnotoad-end.png"
        super().__init__("futurama", "futurama_trivia.json", fry_red, thumb, end_thumb)


class SimpsonsTrivia(TriviaCategory):
    def __init__(self) -> None:
        simpsons_yellow = discord.Colour(0xFFEF06)
        thumb = (
            "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/donut.gif?raw=true"
        )
        end_thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/donut-end.png"
        super().__init__("simpsons", "simpsons_trivia.json", simpsons_yellow, thumb, end_thumb)


class RickAndMortyTrivia(TriviaCategory):
    def __init__(self) -> None:
        rick_blue = discord.Colour(0xAAD3EA)
        thumb = (
            "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/refs/heads/main/gifs/portal.gif?raw=true"
        )
        super().__init__("rickandmorty", "ram_trivia.json", rick_blue, thumb, thumb)
