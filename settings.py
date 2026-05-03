from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    runtime_env: str = Field(default="prd", validation_alias="RUNTIME_ENV")
    agentos_name: str = Field(default="The Ai Buildr - AgentOS", validation_alias="AGENTOS_NAME")
    scheduler_enabled: bool = Field(default=True, validation_alias="SCHEDULER_ENABLED")
    scheduler_poll_interval: int = Field(default=30, validation_alias="SCHEDULER_POLL_INTERVAL")
    tracing: bool = Field(default=True, validation_alias="AGENTOS_TRACING")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached app settings instance."""
    return Settings()

