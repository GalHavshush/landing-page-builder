from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration comes from environment variables (or a .env file); nothing is hard-coded."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILDER_", extra="ignore")

    database_url: str = "postgresql+psycopg://builder:builder@localhost:5432/builder"
    # Cookies are marked Secure outside local development.
    cookie_secure: bool = False
    session_days: int = 14
    allow_registration: bool = True

    # Uploaded files. "local" writes under storage_path (dev); "s3" uses any S3-compatible
    # service (MinIO locally, Cloudflare R2 / AWS S3 in production).
    storage_backend: str = "local"
    storage_path: str = "./data/uploads"
    s3_endpoint_url: str | None = None
    s3_bucket: str = "builder-uploads"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "auto"
    # URL prefix under which uploaded files are reachable by browsers (the API serves
    # /media itself; behind a reverse proxy or CDN this can point elsewhere).
    media_url_prefix: str = "/api/media"
    max_upload_bytes: int = 10 * 1024 * 1024
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
