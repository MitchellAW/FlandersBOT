import discord

from flanders.models import TriviaUserStats


class TriviaUserStatsView(discord.ui.LayoutView):
    def __init__(self, user_stats: TriviaUserStats, user: discord.User | discord.Member) -> None:
        super().__init__()
        stats = f"## 📊 Trivia Statistics\n### {user.mention}\n\n{user_stats}"

        container = discord.ui.Container()

        stats_display = discord.ui.TextDisplay(content=stats)
        if user.avatar is not None and isinstance(user.avatar.url, str):
            thumbnail = discord.ui.Thumbnail(media=user.avatar.url)
            section = discord.ui.Section(accessory=thumbnail)
            section.add_item(stats_display)
            container.add_item(section)

        else:
            container.add_item(stats_display)

        self.add_item(container)
