"""Configuration settings for Sly Fox Tunes bot."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot Configuration
    telegram_bot_token: str

    # File Management
    temp_dir: Path = Path("temp")
    max_file_size_mb: int = 2000

    # YouTube Cookies
    cookies_file: Path | None = None

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
