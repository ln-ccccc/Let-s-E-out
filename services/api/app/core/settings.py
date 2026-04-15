from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    env: Literal["development", "staging", "production"] = "development"
    jwt_secret: str
    jwt_expires_minutes: int = 60 * 24 * 30
    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
