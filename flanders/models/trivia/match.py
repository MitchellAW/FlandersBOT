from dataclasses import dataclass, field

from flanders.models.trivia.category import TriviaCategory
from flanders.models.trivia.question import TriviaQuestion
from flanders.models.trivia.round import TriviaRound


@dataclass
class TriviaMatch:
    host: int
    match_id: int
    questions: list[TriviaQuestion]
    category: TriviaCategory
    jump_url: str

    _current_round: TriviaRound | None = field(default=None, repr=False)
    _completed_rounds: list[TriviaRound] = field(default_factory=list, repr=False)
    _is_idle: bool = False
    _force_ended: bool = False

    def start_round(self) -> TriviaRound | None:
        if self._current_round is not None:
            msg = "A round is already in progress. Call end_round() first."
            raise RuntimeError(msg)
        if not self.questions:
            msg = "A round is already in progress. Call end_round() first."
            raise RuntimeError(msg)

        question = self.questions.pop()
        self._current_round = TriviaRound(question=question)
        return self._current_round

    def end_round(self) -> TriviaRound:
        if self._current_round is None:
            msg = "No round is currently in progress."
            raise RuntimeError(msg)

        completed = self._current_round
        self._completed_rounds.append(completed)
        completed.end_round()
        self._current_round = None
        return completed

    def end_match_due_to_inactivity(self) -> None:
        self._is_idle = True

    def force_end_match(self) -> None:
        self._force_ended = True

    @property
    def current_round(self) -> TriviaRound | None:
        return self._current_round

    @property
    def completed_rounds(self) -> list[TriviaRound]:
        return list(self._completed_rounds)

    @property
    def is_finished(self) -> bool:
        """True when all questions have been played and no round is open."""
        return self._is_idle or self._force_ended or (not self.questions and self._current_round is None)

    def was_force_ended(self) -> bool:
        return self._force_ended

    def questions_remaining(self) -> int:
        return len(self.questions)

    def rounds_played(self) -> int:
        return len(self._completed_rounds)
