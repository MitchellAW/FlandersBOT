import discord

from flanders.models import TriviaLeaderboardEntry, TriviaLeaderboardType


class TriviaLeaderboardView(discord.ui.LayoutView):
    def __init__(
        self,
        leaderboard: dict[TriviaLeaderboardType, list[TriviaLeaderboardEntry]],
        thumbnail_url: str,
        footer: str,
    ) -> None:
        super().__init__()

        self.leaderboard = leaderboard
        self.thumbnail_url = thumbnail_url
        self.footer = footer

        self.action_row = discord.ui.ActionRow()
        self.dropdown = TriviaDropdown()
        self.action_row.add_item(self.dropdown)
        self.add_item(self.action_row)

        container = discord.ui.Container()

        self.display = discord.ui.TextDisplay(content=self.category_content(TriviaLeaderboardType.SCORE))

        thumbnail = discord.ui.Thumbnail(media=self.thumbnail_url)
        section = discord.ui.Section(accessory=thumbnail)
        section.add_item(self.display)
        container.add_item(section)
        self.add_item(container)

    def category_content(self, category: TriviaLeaderboardType) -> str:
        stats = {
            TriviaLeaderboardType.SCORE: "🏆 High Scores",
            TriviaLeaderboardType.WINS: "🥇 Wins",
            TriviaLeaderboardType.CORRECT_ANSWERS: "✅  Correct Answers",
            TriviaLeaderboardType.FASTEST_ANSWER: "☝️ Fastest Answers",
            TriviaLeaderboardType.LONGEST_STREAK: "🍀 Longest Streak",
        }
        board = f"## {stats.get(category)}\n\n"
        scorers = self.leaderboard.get(category, [])

        board += "\n".join(
            f"{i}. **{entry.username}**: {entry.value if isinstance(entry.value, str) else f'{entry.value:,}'}"
            for i, entry in enumerate(scorers)
        )

        return f"{board}\n\n-# {self.footer}"

    def change_category(self, category: TriviaLeaderboardType) -> None:
        self.display.content = self.category_content(category)


class TriviaDropdown(discord.ui.Select):
    def __init__(self) -> None:
        self.view: TriviaLeaderboardView
        options = [
            discord.SelectOption(
                label="Score",
                emoji="🏆",
                value=TriviaLeaderboardType.SCORE,
                description="The amount of points scored",
                default=True,
            ),
            discord.SelectOption(
                label="Wins",
                emoji="🥇",
                value=TriviaLeaderboardType.WINS,
                description="The number of trivia matches won.",
            ),
            discord.SelectOption(
                label="Correct Answers",
                emoji="✅",
                value=TriviaLeaderboardType.CORRECT_ANSWERS,
                description="The number of correct answers.",
            ),
            discord.SelectOption(
                label="Fastest Answers",
                emoji="☝️",
                value=TriviaLeaderboardType.FASTEST_ANSWER,
                description="The fastest recorded answer times.",
            ),
            discord.SelectOption(
                label="Longest Streaks",
                emoji="🍀",
                value=TriviaLeaderboardType.LONGEST_STREAK,
                description="The longest recorded streaks of correct answers in a row.",
            ),
        ]

        super().__init__(placeholder="Choose a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None or not isinstance(self.view, TriviaLeaderboardView):
            msg = "Dropdown must be added to a TriviaLeaderboardView before its callback can be invoked"
            raise ValueError(msg)

        await interaction.response.defer(ephemeral=True)
        category = TriviaLeaderboardType(self.values[0])
        for option in self.options:
            option.default = option.value in self.values

        self.view.change_category(category=category)
        await interaction.edit_original_response(view=self.view)
