import json
import random
from dataclasses import dataclass, field

import discord
from pydantic import BaseModel
from pydantic.functional_validators import model_validator

REQUIRED_ANSWERS = 3


class TriviaAnswerRecord:
    user_id: int
    is_correct: bool
    elapsed_milliseconds: int


class TriviaQuestion(BaseModel, frozen=True):
    id: int
    question: str
    answers: tuple[str, str, str]
    source: str
    shuffled_answers: tuple[str, str, str]
    correct_index: int

    @model_validator(mode="before")
    @classmethod
    def derived_fields(cls, data) -> list[str]:
        answers = data["answers"]
        shuffled = random.sample(answers, len(answers))
        if "shuffled_answers" not in data:
            data["shuffled_answers"] = tuple(shuffled)

        if "correct_index" not in data:
            data["correct_index"] = shuffled.index(answers[0])

        return data

    @property
    def correct_answer(self) -> str:
        return self.answers[0]


@dataclass()
class TriviaCategory:
    category_name: str
    file_name: str
    colour: discord.Colour
    thumbnail_url: str
    end_thumbnail_url: str

    def load_questions(self) -> list[TriviaQuestion]:
        with open(f"flanders/cogs/data/{self.file_name}", "r") as trivia_data:
            questions = json.load(trivia_data)
            trivia_questions = [TriviaQuestion(id=i, **question) for i, question in enumerate(questions)]
            return random.sample(trivia_questions, len(trivia_questions))


class FuturamaTrivia(TriviaCategory):
    def __init__(self):
        fry_red = discord.Colour(0x9B2525)
        thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/hypnotoad-timer.gif"
        end_thumb = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/hypnotoad-end.png"
        super().__init__("futurama", "futurama_trivia.json", fry_red, thumb, end_thumb)


class SimpsonsTrivia(TriviaCategory):
    def __init__(self):
        simpsons_yellow = discord.Colour(0xFFEF06)
        thumbnail = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/donut-timer.gif"
        end_thumbnail = "https://raw.githubusercontent.com/MitchellAW/MitchellAW.github.io/master/images/donut-end.png"
        super().__init__("simpsons", "simpsons_trivia.json", simpsons_yellow, thumbnail, end_thumbnail)


class RickAndMortyTrivia(TriviaCategory):
    def __init__(self):
        rick_blue = discord.Colour(0xAAD3EA)
        thumbnail = (
            "https://github.com/MitchellAW/MitchellAW.github.io/blob/master/images/rick-morty-portal.gif?raw=true"
        )
        super().__init__("rickandmorty", "ram_trivia.json", rick_blue, thumbnail, thumbnail)


@dataclass
class TriviaSession:
    match_id: int
    trivia_questions: list[TriviaQuestion]
    category: TriviaCategory
    asked_questions: list[TriviaQuestion] = field(default_factory=list)

    def next_question(self) -> TriviaQuestion | None:
        if len(self.trivia_questions) > 0:
            question = self.trivia_questions.pop()
            self.asked_questions.append(question)
            return question
        else:
            return None

    def current_question(self) -> TriviaQuestion | None:
        if len(self.asked_questions) > 0:
            return self.asked_questions[-1]

        else:
            return None

    def questions_remaining(self) -> int:
        return len(self.trivia_questions)

    def questions_asked(self) -> int:
        return len(self.asked_questions)
