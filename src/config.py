from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str | None = None  # Optional: for local migrations, falls back to DATABASE_URL

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Dezztech Backend"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


# Singleton instance
settings = Settings()
