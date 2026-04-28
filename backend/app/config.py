from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LYRIC_ASSISTANT_", case_sensitive=False)

    token: str
    database_url: str
    version: str = "0.1.0"

    @property
    def sync_database_url(self) -> str:
        # Alembic uses sync driver; runtime uses asyncpg.
        return self.database_url.replace("+asyncpg", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
