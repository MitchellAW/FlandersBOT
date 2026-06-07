import random
from dataclasses import dataclass

from pydantic import BaseModel, model_validator


@dataclass
class TriviaAnswer:
    user_id: int
    username: str
    mention: str
    answer_index: int
    is_correct: bool
    answer_time: int


class TriviaQuestion(BaseModel, frozen=True):
    id: int
    question: str
    answers: tuple[str, str, str]
    source: str
    shuffled_answers: tuple[str, str, str]
    correct_index: int

    @model_validator(mode="before")
    @classmethod
    def derived_fields(cls, data: dict) -> dict:
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
