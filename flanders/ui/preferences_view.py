from abc import abstractmethod

import compuglobal
import discord

from flanders.models import AVAILABLE_COLORS, UserPreferenceState, UserSearchPreferences


class PreferencesView(discord.ui.LayoutView):
    def __init__(
        self,
        state: UserPreferenceState,
        image_url: str,
    ) -> None:
        super().__init__()
        self.state = state
        self.image_url = image_url

        self.preview = discord.ui.MediaGallery()

        # Action rows

        # Add preview image
        self.add_item(discord.ui.TextDisplay(content="## Your Preferences\n### Preview:"))
        self.preview.add_item(media=image_url)
        self.add_item(self.preview)

        # Subtitle/Font preferences
        self.add_item(discord.ui.TextDisplay(content="### Subtitle Preferences:"))

        # Add Font family select
        self.add_item(discord.ui.TextDisplay(content="-# Font:"))
        allowed_fonts = self.state.api.config.allowed_fonts.copy()
        font_options = [
            FontFamilyOption(
                font_family=font,
                default=font == self.state.overlay_prefs.font_family,
                description="Default" if font == self.state.overlay_prefs.font_family else None,
            )
            for font in allowed_fonts
        ]
        font_family_row = discord.ui.ActionRow()
        font_family_select = FontFamilyDropdown(font_options=font_options, state=self.state)
        font_family_row.add_item(font_family_select)
        self.add_item(font_family_row)

        # Add font size select
        self.add_item(discord.ui.TextDisplay(content="-# Font size:"))
        font_size_row = discord.ui.ActionRow()
        font_size_select = FontSizeDropdown(state=self.state)
        font_size_row.add_item(font_size_select)
        self.add_item(font_size_row)

        # Add font color select
        self.add_item(discord.ui.TextDisplay(content="-# Font color:"))
        color_options = [
            FontColorOption(
                color_name=color_name,
                font_color=font_color,
                default=font_color == self.state.overlay_prefs.font_color,
                description="Default" if font_color == self.state.overlay_prefs.font_color else None,
            )
            for color_name, font_color in AVAILABLE_COLORS.items()
        ]
        font_color_select = FontColorDropdown(color_options=color_options, state=self.state)
        font_color_row = discord.ui.ActionRow()
        font_color_row.add_item(font_color_select)
        self.add_item(font_color_row)

        # Add toggle button row
        toggle_button_row = discord.ui.ActionRow()
        toggle_uppercase = ToggleUppercaseModeButton(state=self.state)
        toggle_advanced = ToggleAdvancedModeButton(state=self.state)
        toggle_button_row.add_item(toggle_uppercase)
        toggle_button_row.add_item(toggle_advanced)
        self.add_item(toggle_button_row)

        # Search preferences
        self.add_item(
            discord.ui.TextDisplay(
                content="### Search preferences:\n-# Select a minimum and a maximum season to filter by:",
            ),
        )

        season_row = discord.ui.ActionRow()
        season_dropdown = SeasonDropdown(state=self.state)
        season_row.add_item(season_dropdown)
        self.add_item(season_row)

        # Add save button
        primary_button_row = discord.ui.ActionRow()
        save_button = SavePreferencesButton()
        primary_button_row.add_item(save_button)

        # Add restore defaults button
        restore_button = RestoreDefaultPreferencesButton()
        primary_button_row.add_item(restore_button)
        self.add_item(primary_button_row)

    async def restore_defaults(self) -> None:
        self.state.restore_defaults()
        for child in self.walk_children():
            if isinstance(child, (PreferenceDropdown, ToggleButton)):
                child.restore_defaults()
        await self.update_image()

    async def update_image(self) -> None:
        new_image_url = await self.state.regenerate_image_url()
        self.image_url = new_image_url
        self.preview.clear_items()
        self.preview.add_item(media=self.image_url)

    def disable_all(self) -> None:
        for child in self.walk_children():
            if isinstance(child, (discord.ui.Button, discord.ui.Select)):
                child.disabled = True


class PreferenceDropdown(discord.ui.Select):
    @abstractmethod
    def restore_defaults(self) -> None:
        pass


class FontColorOption(discord.SelectOption):
    def __init__(self, color_name: str, font_color: compuglobal.FontColor, **kwargs) -> None:  # noqa: ANN003
        self.font_color = font_color

        super().__init__(label=color_name, **kwargs)


class FontColorDropdown(PreferenceDropdown):
    def __init__(self, color_options: list[FontColorOption], state: UserPreferenceState) -> None:
        self.state = state
        self.color_options = color_options
        super().__init__(options=list(color_options), placeholder="Select a color...")

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Dropdown must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        chosen_color = self.color_options[0]
        for color_option, option in zip(self.color_options, self.options, strict=True):
            if option.value == self.values[0]:
                chosen_color = color_option.font_color
            option.default = option.value in self.values

        if len(self.values) > 0:
            self.state.overlay_prefs = self.state.overlay_prefs.model_copy(
                update={"font_color": chosen_color},
            )

        await self.view.update_image()

        await interaction.edit_original_response(view=self.view)

    def restore_defaults(self) -> None:
        for color_option, option in zip(self.color_options, self.options, strict=True):
            option.default = color_option.font_color == self.state.api.config.default_format.font_color


class FontFamilyOption(discord.SelectOption):
    def __init__(self, font_family: compuglobal.FontFamily, **kwargs) -> None:  # noqa: ANN003
        self.font_family = font_family

        font_family_names: dict[compuglobal.FontFamily, str] = {
            compuglobal.FontFamily.AKBAR: "Akbar",
            compuglobal.FontFamily.FR_BOLD: "Fr Bold",
            compuglobal.FontFamily.IMPACT: "Impact",
            compuglobal.FontFamily.COMIC_NEUE: "Comic Neue",
            compuglobal.FontFamily.PACIFICO: "Pacifico",
            compuglobal.FontFamily.JOST: "Jost",
        }

        super().__init__(label=f"{font_family_names.get(font_family, 'Unknown Font')}", **kwargs)


class FontFamilyDropdown(PreferenceDropdown):
    def __init__(self, font_options: list[FontFamilyOption], state: UserPreferenceState) -> None:
        self.state = state
        self.font_options = font_options
        super().__init__(options=list(font_options), placeholder="Select a font...")

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Dropdown must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        chosen_font = self.font_options[0]
        for font_option, option in zip(self.font_options, self.options, strict=True):
            if option.value == self.values[0]:
                chosen_font = font_option.font_family
            option.default = option.value in self.values

        if len(self.values) > 0:
            self.state.overlay_prefs = self.state.overlay_prefs.model_copy(
                update={"font_family": chosen_font},
            )

        await self.view.update_image()

        await interaction.edit_original_response(view=self.view)

    def restore_defaults(self) -> None:
        for font_option, option in zip(self.font_options, self.options, strict=True):
            option.default = font_option.font_family == self.state.api.config.default_format.font_family


class FontSizeDropdown(PreferenceDropdown):
    def __init__(self, state: UserPreferenceState) -> None:
        self.state = state

        self.default_font_size = 0
        allowed_font_sizes = [self.default_font_size, *list(range(32, 121, 8))]
        size_options = [
            discord.SelectOption(
                label=str(font_size) if font_size != 0 else "Auto",
                value=str(font_size),
                description="Default" if font_size == self.state.overlay_prefs.font_size else None,
                default=font_size == self.state.overlay_prefs.font_size,
            )
            for font_size in allowed_font_sizes
        ]
        super().__init__(options=size_options, placeholder="Select a font size...")

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Dropdown must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        for option in self.options:
            option.default = option.value in self.values

        if len(self.values) > 0:
            self.state.overlay_prefs = self.state.overlay_prefs.model_copy(
                update={"font_size": int(self.values[0])},
            )
        await self.view.update_image()
        await interaction.edit_original_response(view=self.view)

    def restore_defaults(self) -> None:
        for option in self.options:
            option.default = option.value == str(self.default_font_size)


class SeasonDropdown(PreferenceDropdown):
    def __init__(self, state: UserPreferenceState) -> None:
        self.state = state
        seasons = self.state.evenly_spaced_seasons()[:25]
        chosen_seasons = (self.state.search_prefs.season_min, self.state.search_prefs.season_max)
        season_options = [
            discord.SelectOption(
                label=f"{season if season != 0 else '0 - Movies'}",
                value=str(season),
                default=season in chosen_seasons,
            )
            for season in seasons
        ]

        super().__init__(options=season_options, placeholder="No season filters chosen...", min_values=2, max_values=2)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Dropdown must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        for option in self.options:
            option.default = option.value in self.values

        if len(self.values) >= self.max_values:
            sorted_values = sorted(self.values)
            season_min, season_max = int(sorted_values[0]), int(sorted_values[1])
            self.state.search_prefs = UserSearchPreferences(season_min=season_min, season_max=season_max)

        await self.view.update_image()
        await interaction.edit_original_response(view=self.view)

    def restore_defaults(self) -> None:
        for option in self.options:
            option.default = False


class SavePreferencesButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Save Preferences", emoji="💾", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Button must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        self.view.disable_all()
        await interaction.edit_original_response(view=self.view)
        await self.view.state.update_user_preferences()


class RestoreDefaultPreferencesButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(label="Restore Defaults", emoji="🗑️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Button must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        await self.view.restore_defaults()
        await interaction.edit_original_response(view=self.view)


class ToggleButton(discord.ui.Button):
    toggled_on = discord.ButtonStyle.success
    toggled_off = discord.ButtonStyle.secondary

    @abstractmethod
    def get_style(self) -> discord.ButtonStyle:
        pass

    @abstractmethod
    def toggle_state(self) -> None:
        pass

    def restore_defaults(self) -> None:
        self.style = self.get_style()

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        if self.view is None or not isinstance(self.view, PreferencesView):
            msg = "Button must be added to a PreferencesView before its callback can be invoked"
            raise ValueError(msg)

        self.toggle_state()
        self.style = self.get_style()
        await self.view.update_image()
        await interaction.edit_original_response(view=self.view)


class ToggleAdvancedModeButton(ToggleButton):
    def __init__(self, state: UserPreferenceState) -> None:
        self.state = state
        super().__init__(label="Advanced Mode", emoji="🛠️", style=self.get_style())

    def get_style(self) -> discord.ButtonStyle:
        return self.toggled_on if self.state.advanced else self.toggled_off

    def toggle_state(self) -> None:
        self.state.advanced = not self.state.advanced


class ToggleUppercaseModeButton(ToggleButton):
    def __init__(self, state: UserPreferenceState) -> None:
        self.state = state
        super().__init__(label="All Caps", emoji="⬆️", style=self.get_style())

    def get_style(self) -> discord.ButtonStyle:
        return self.toggled_on if self.state.overlay_prefs.all_caps else self.toggled_off

    def toggle_state(self) -> None:
        self.state.overlay_prefs = self.state.overlay_prefs.model_copy(
            update={"all_caps": not self.state.overlay_prefs.all_caps},
        )
