from dataclasses import dataclass


@dataclass
class TriviaUserStat:
    rank: int
    value: int | float

    def __str__(self) -> str:
        if isinstance(self.value, float):
            return f"(#{self.rank})**: {self.value:.2f}"
        return f"(#{self.rank})**: {self.value:,}"


@dataclass
class TriviaUserStats:
    score: TriviaUserStat
    wins: TriviaUserStat
    losses: TriviaUserStat
    correct_answers: TriviaUserStat
    incorrect_answers: TriviaUserStat
    fastest_answer: TriviaUserStat
    current_streak: TriviaUserStat
    longest_streak: TriviaUserStat

    def __str__(self) -> str:
        accuracy = self.correct_answers.value / self.correct_answers.value + self.incorrect_answers.value
        return (
            f"🏆 **Score {self.score}\n\n"
            f"🥇 **Wins {self.wins}\n\n"
            f"💩 **Losses {self.losses}\n\n"
            f"✅ **Correct Answers {self.correct_answers}\n\n"
            f"🏹 **Accuracy**: {accuracy:.2f}%\n\n"
            f"☝️ **Fastest Answer**: (#{self.fastest_answer.rank}): {self.fastest_answer.value / 1000:.3f}s\n\n"
            f"📈 **Current Streak {self.current_streak}\n\n"
            f"🍀 **Longest Streak {self.longest_streak}"
        )
