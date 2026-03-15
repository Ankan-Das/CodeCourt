"""Configuration management for CodeCourt."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM Provider API Keys (loaded from .env file or environment)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_host: str = "http://localhost:11434"

    # Default models for each role
    defender_model: str = "gpt-4o"
    prosecutor_model: str = "gpt-4o"
    judge_model: str = "claude-3-5-sonnet-20241022"
    security_model: str = "claude-3-5-sonnet-20241022"

    # Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: str = "INFO"
    debug: bool = False


settings = Settings()
