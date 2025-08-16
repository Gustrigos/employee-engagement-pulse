from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: Optional[str] = None
    cors_allow_origins: list[str] = ["*"]

    # Slack OAuth / API configuration
    slack_client_id: Optional[str] = None
    slack_client_secret: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    slack_redirect_uri: Optional[str] = None
    # Comma-separated scopes for the bot token; Slack expects a comma-delimited string
    slack_bot_scopes: str = (
        "channels:read,groups:read,chat:write,users:read,emoji:read,"
        "channels:history,groups:history"
    )
    # Optional user scopes if needed in the future
    slack_user_scopes: Optional[str] = None

    # Anthropic configuration
    anthropic_api_key: Optional[str] = None
    anthropic_default_model: str = "claude-3-5-sonnet-20240620"
    anthropic_max_tokens: int = 1024
    anthropic_default_temperature: float = 0.2
    anthropic_disable_fallback: bool = False
    anthropic_api_base: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

# Backwards-compat module-level settings object used by some modules/tests
settings = get_settings()
