from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pooled connection (Neon PgBouncer endpoint), used by the app at runtime.
    # A harmless placeholder keeps imports working before a real `.env` exists;
    # the engine is lazy and never connects on import.
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/placeholder"

    # Direct/non-pooled connection, used by Alembic migrations.
    database_url_direct: str | None = None

    app_env: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
