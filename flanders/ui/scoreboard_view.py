import discord

from flanders.models import TriviaCategory, TriviaScoreboard


class TriviaScoreboardView(discord.ui.LayoutView):
    def __init__(self, scoreboard: TriviaScoreboard | None, trivia_category: TriviaCategory) -> None:
        super().__init__()

        container = discord.ui.Container()
        thumb = discord.ui.Thumbnail(media=trivia_category.thumbnail_url)
        section = discord.ui.Section(accessory=thumb)

        text_display = discord.ui.TextDisplay(content=f"{scoreboard}")
        section.add_item(text_display)

        container.add_item(section)
        self.add_item(container)
