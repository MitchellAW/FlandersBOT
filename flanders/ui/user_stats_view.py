import discord


class TriviaUserStatsView(discord.ui.LayoutView):
    def __init__(self, user_stats: dict[str, int], user: discord.User | discord.Member) -> None:
        super().__init__()
        accuracy = user_stats["correct_answers"] / (user_stats["incorrect_answers"] + user_stats["correct_answers"])
        stats = (
            "## 📊 Trivia Statistics\n"
            f"### {user.mention}\n\n"
            f"🏆 **Score (#{user_stats['score_rank']})**: {user_stats['score']:,}\n\n"
            f"🥇 **Wins (#{user_stats['wins_rank']})**: {user_stats['wins']}\n\n"
            f"💩 **Losses (#{user_stats['losses_rank']})**: {user_stats['losses']}\n\n"
            f"✅ **Correct Answers (#{user_stats['correct_answers_rank']})**: {user_stats['correct_answers']}\n\n"
            f"🏹 **Accuracy**: {accuracy:.2f}%\n\n"
            f"☝️ **Fastest Answer (#{user_stats['fastest_answer_rank']})**: "
            f"{user_stats['fastest_answer'] / 1000:.3f}s\n\n"
            f"📈 **Current Streak (#{user_stats['current_streak_rank']})**: {user_stats['current_streak']}\n\n"
            f"🍀 **Longest Streak (#{user_stats['longest_streak_rank']})**: {user_stats['longest_streak']}"
        )

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
