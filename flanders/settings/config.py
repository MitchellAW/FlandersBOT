import logging
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class FlandersConfig(BaseSettings, frozen=True):
    # Use .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Bot configuration
    bot_token: str
    owner_id: int
    debug_mode: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL"] = "INFO"

    # Database configuration
    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgres://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def log_level_int(self) -> int:
        levels = logging.getLevelNamesMapping()
        return levels.get(self.log_level, 20)
