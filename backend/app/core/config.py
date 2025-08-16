from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
	# App
	app_name: str = Field(default="employee-pulse", alias="APP_NAME")

	# Anthropic
	anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
	anthropic_model: str = Field(default="claude-3-5-sonnet-20240620", alias="ANTHROPIC_MODEL")
	anthropic_max_tokens: int = Field(default=1024, alias="ANTHROPIC_MAX_TOKENS")

	class Config:
		env_file = ".env"
		case_sensitive = False


settings = Settings()