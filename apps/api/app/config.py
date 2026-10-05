from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration comes from environment variables (or a .env file); nothing is hard-coded."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILDER_", extra="ignore")

    database_url: str = "postgresql+psycopg://builder:builder@localhost:5432/builder"
    # Cookies are marked Secure outside local development.
    cookie_secure: bool = False
    session_days: int = 14
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
