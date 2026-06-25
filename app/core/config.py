"""Application configuration loaded from environment variables.

Mirrors GreenX 2.0's `app/core/config.py` pattern but stripped to the SMS
domain — no InfluxDB / OpenAI / network thresholds.
"""

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    # --- App metadata ---
    APP_NAME: str = "School Management API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Professional API for the School Management System"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = Field(default="development", description="development | staging | production")
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:@localhost:3306/school_management",
        description="SQLAlchemy DSN for the primary MySQL database",
    )

    # --- JWT / Security ---
    SECRET_KEY: str = Field(
        default="change-me-in-production-this-is-not-a-real-secret",
        description="HMAC key used to sign JWT access tokens",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    PASSWORD_MIN_LENGTH: int = 8

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # --- Default admin (created on first boot if no superuser exists) ---
    DEFAULT_ADMIN_EMAIL: str = "admin@sms.com"
    DEFAULT_ADMIN_PASSWORD: str = "Admin@12345"
    DEFAULT_ADMIN_NAME: str = "System Administrator"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor. Use this everywhere instead of re-instantiating."""
    return Settings()


# Module-level instance for direct imports: `from app.core.config import settings`
settings = get_settings()
