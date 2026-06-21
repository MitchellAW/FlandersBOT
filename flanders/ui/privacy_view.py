import discord

from flanders.utils import TriviaDB, get_view_as


class TriviaPrivacyView(discord.ui.LayoutView):
    def __init__(self, privacy_setting: int, trivia_db: TriviaDB) -> None:
        super().__init__()
        self.ALLOWED_CHANGES = 4
        self.HEADER = "## Privacy and Data Collection\n"

        self.privacy_setting = privacy_setting
        self.trivia_db = trivia_db
        self.change_count = 0

        self.policy_button = discord.ui.Button(
            label="Privacy Policy",
            url="https://github.com/MitchellAW/FlandersBOT/blob/main/privacy-policy.md",
        )

        self.action_row = discord.ui.ActionRow()
        self.action_row.add_item(TriviaPrivacyToggleButton())
        self.action_row.add_item(self.policy_button)
        self.action_row.add_item(TriviaPrivacyDeleteButton())

        self.repopulate_self()

    async def toggle_privacy_setting(self, user_id: int) -> None:
        self.change_count += 1
        self.privacy_setting = 0 if self.privacy_setting else 1

        await self.trivia_db.set_user_privacy_setting(user_id=user_id, privacy_setting=self.privacy_setting)

        self.repopulate_self()

    async def delete_data(self, user_id: int) -> None:
        self.clear_items()
        content = f"{self.HEADER}\nAll of your data has been deleted.\nTry `/trivia stats` to confirm the deletion."
        text_display = discord.ui.TextDisplay(content=content)
        self.add_item(text_display)
        action_row = discord.ui.ActionRow()
        action_row.add_item(self.policy_button)
        self.add_item(action_row)

        await self.trivia_db.delete_all_user_data(user_id=user_id)

    def disable_buttons(self) -> None:
        for button in self.action_row.walk_children():
            if isinstance(button, discord.ui.Button) and button.url is None:
                button.disabled = True

    def repopulate_self(self) -> None:
        self.clear_items()
        content = (
            "## Privacy and Data Collection\n"
            "You are currently "
            f"{
                '**hidden** from all leaderboards.\n'
                if self.privacy_setting == 1
                else '**visible** in all leaderboards.\n'
            }"
            "You can toggle your visibility within the leaderboards using the **Toggle Privacy** button.\n\n"
            "If you would like all of your data to be deleted, you can "
            "use the **Delete My Data** button."
            "\n-# :warning: Warning: This action cannot be undone.\n\n"
            "You can also click the **Privacy Policy** button to review the privacy policy of Flanders.\n"
        )
        text_display = discord.ui.TextDisplay(content=content)
        self.add_item(text_display)
        self.add_item(self.action_row)


class TriviaPrivacyToggleButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Toggle Privacy", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = get_view_as(self.view, TriviaPrivacyView)

        await interaction.response.defer()
        if view.change_count < view.ALLOWED_CHANGES:
            await view.toggle_privacy_setting(user_id=interaction.user.id)

        else:
            view.disable_buttons()

        await interaction.edit_original_response(view=view)


class TriviaPrivacyDeleteButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Delete My Data", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = get_view_as(self.view, TriviaPrivacyView)
        modal = TriviaDataDeletionModal(view=view)
        await interaction.response.send_modal(modal)


class TriviaDataDeletionModal(discord.ui.Modal):
    def __init__(self, view: TriviaPrivacyView) -> None:
        super().__init__(title="Confirm Data Deletion")
        self.view = view

        text_display = discord.ui.TextDisplay(
            content=(
                "By confirming below, you understand that all of your data will be permanently deleted. "
                "This includes all of your progress being removed from the leaderboards.\n\n"
                "-# :warning: This action cannot be undone."
            ),
        )
        self.add_item(text_display)
        self.confirmation = discord.ui.Checkbox(default=False)
        self.confirmation_label = discord.ui.Label(
            text="Yes, permanently delete all of my data.",
            component=self.confirmation,
        )
        self.add_item(self.confirmation_label)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.confirmation.value:
            await interaction.response.defer()
            await self.view.delete_data(interaction.user.id)
            await interaction.edit_original_response(view=self.view)
