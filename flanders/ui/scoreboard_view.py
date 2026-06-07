import discord

from flanders.models import TriviaCategory, TriviaScoreboard


class TriviaScoreboardView(discord.ui.LayoutView):
    def __init__(self, scoreboard: TriviaScoreboard | None, trivia_category: TriviaCategory) -> None:
        super().__init__()

        container = discord.ui.Container()
        thumb = discord.ui.Thumbnail(media=trivia_category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)

        content = "## Trivia Scoreboard"

        if scoreboard is None or scoreboard.participant_count == 0:
            content += "\nUnfortunately, there were no participants in the trivia."

        else:
            top_scorers = scoreboard.top_scorers
            scorer_id, score = top_scorers[0]

            content += f"\nCongratulations to the top scorer, **<@!{scorer_id}>**!"

            # List scorers
            scorers = "\n\n### :medal: Correct Answers\n"
            for i, (scorer_id, score) in enumerate(scoreboard.top_scorers[:5]):
                scorers += f"{i}. <@!{scorer_id}>: {round(score, 2):,}\n"

            content += scorers

            # List highest accuracies
            scorers = "\n### :bow_and_arrow: Highest Accuracy\n"
            for i, (scorer_id, score) in enumerate(scoreboard.highest_accuracy[:5]):
                scorers += f"{i}. <@!{scorer_id}>: {round(score * 100.0, 2):,}%\n"
            content += scorers

            # List Fastest Answers
            scorers = "\n### :point_up: Fastest Answers\n"
            scorers += "-----\n" if len(scoreboard.fastest_answers) == 0 else ""
            for i, (scorer_id, score) in enumerate(scoreboard.fastest_answers[:5]):
                scorers += f"{i}. <@!{scorer_id}>: {round(score / 1000, 3):,}s\n"
            content += scorers

            content += (
                f"\n-# {scoreboard.participant_count} participant{'s' if scoreboard.participant_count > 1 else ''}, "
                f"{scoreboard.question_count} question{'s' if scoreboard.question_count > 1 else ''} answered."
            )

        text_display = discord.ui.TextDisplay(content=content)
        section.add_item(text_display)

        container.add_item(section)
        self.add_item(container)
