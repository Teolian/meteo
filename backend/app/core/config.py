"""Application configuration."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Ice Fishing Bite Index API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Timezone
    tz: str = "Europe/Moscow"

    # API Keys and User Agents
    openweather_key: str = ""
    metno_user_agent: str = "IceFishingApp/0.1 (contact: user@example.com)"

    # Database
    database_url: str = "sqlite:///./data/meteo.db"

    # Cache settings
    cache_ttl_minutes: int = 60
    cache_max_size: int = 128

    # Weather providers
    enable_open_meteo: bool = True
    enable_metno: bool = True
    enable_openweather: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
