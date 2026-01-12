"""Application configuration using Pydantic v2 settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    api_env: Literal["development", "production", "test"] = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    secret_key: str = Field(
        default="dev_secret_key_CHANGE_IN_PRODUCTION",
        min_length=32,
    )

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://decisioncalm:password@localhost:5432/decisioncalm"
    )

    # OpenAI
    openai_api_key: str = Field(default="")
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_retries: int = 3
    openai_timeout: int = 60

    # Redis (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_enabled: bool = False

    # Security & CORS
    allowed_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 30

    # Feature Flags
    enable_vector_search: bool = True
    enable_observability: bool = False

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.api_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.api_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
