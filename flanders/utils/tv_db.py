import asyncpg
from compuglobal import AsyncCompuGlobalAPI, OverlayFormat

from flanders.models import UserPreferences, UserSearchPreferences


class PreferencesDB:
    def __init__(self, db: asyncpg.Pool) -> None:
        self.db = db

    async def get_user_preferences(
        self,
        user_id: int,
        tv_show: str,
        api: AsyncCompuGlobalAPI,
    ) -> UserPreferences:
        query = """SELECT overlay_preferences, search_preferences, advanced_mode
                   FROM user_preferences WHERE user_id = $1 AND tv_show = $2"""
        result = await self.db.fetchrow(query, user_id, tv_show)
        if result is None:
            return UserPreferences(user_id=user_id, tv_show=tv_show, overlay_preferences=api.config.default_format)

        return UserPreferences(
            user_id=user_id,
            tv_show=tv_show,
            search_preferences=UserSearchPreferences.model_validate_json(result["search_preferences"]),
            overlay_preferences=OverlayFormat.model_validate_json(result["overlay_preferences"]),
            advanced_mode=result["advanced_mode"],
        )

    async def update_user_preferences(self, user_preferences: UserPreferences) -> None:
        query = """INSERT INTO user_preferences (
                       user_id, tv_show, overlay_preferences, search_preferences, advanced_mode
                   )
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (user_id, tv_show)
                   DO UPDATE SET overlay_preferences = EXCLUDED.overlay_preferences,
                   search_preferences = EXCLUDED.search_preferences,
                   advanced_mode = EXCLUDED.advanced_mode
                   """
        await self.db.execute(
            query,
            user_preferences.user_id,
            user_preferences.tv_show,
            user_preferences.overlay_preferences.model_dump_json(exclude_defaults=True),
            user_preferences.search_preferences.model_dump_json(exclude_defaults=True),
            user_preferences.advanced_mode,
        )
