from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/api directory, independent of the process's current working directory,
# so the API server and standalone scripts (e.g. the seed generator) always
# resolve the default SQLite file to the same absolute path.
API_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{(API_ROOT / 'skillgraph.db').as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SkillGraph API"
    environment: str = "development"

    database_url: str = DEFAULT_SQLITE_URL

    jwt_secret: str = "dev-only-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    cors_origins: list[str] = ["http://localhost:3000"]

    ai_provider: str = "mock"  # mock | anthropic | openai | google
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None

    rate_limit_per_minute: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
