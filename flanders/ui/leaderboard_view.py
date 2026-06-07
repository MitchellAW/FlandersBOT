import discord

from flanders.models import TriviaLeaderboardEntry, TriviaLeaderboardType


class TriviaLeaderboardView(discord.ui.LayoutView):
    def __init__(
        self,
        leaderboard: dict[TriviaLeaderboardType, list[TriviaLeaderboardEntry]],
        thumbnail_url: str | None,
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

        self.change_category(category=TriviaLeaderboardType.SCORE)

    def change_category(self, category: TriviaLeaderboardType) -> None:
        self.clear_items()
        self.add_item(self.action_row)

        container = discord.ui.Container()

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

        category_content = discord.ui.TextDisplay(content=f"{board}\n\n-# {self.footer}")

        if self.thumbnail_url is not None:
            thumbnail = discord.ui.Thumbnail(media=self.thumbnail_url)
            section = discord.ui.Section(accessory=thumbnail)
            section.add_item(category_content)
            container.add_item(section)

        else:
            container.add_item(category_content)

        self.add_item(container)


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
        if self.view is None:
            msg = "Dropdown must be added to a view before its callback can be invoked"
            raise ValueError(msg)

        await interaction.response.defer(ephemeral=True)
        category = TriviaLeaderboardType.SCORE
        for option in self.options:
            if option.value == self.values[0]:
                category = TriviaLeaderboardType(option.value)
                option.default = True

            else:
                option.default = False

        self.view.change_category(category=category)
        await interaction.edit_original_response(view=self.view)
