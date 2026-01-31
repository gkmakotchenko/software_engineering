from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Put these variables into a `.env` file for local development.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Telegram
    telegram_bot_token: str

    # Summarization backend
    # Prefer HF Inference API (no heavy model hosting) if token is provided.
    hf_api_token: str | None = None
    hf_model_id: str = "facebook/bart-large-cnn"  # Russian abstractive summarization
    hf_timeout_s: int = 60

    # Limits (Telegram messages can be long; keep sane defaults)
    max_input_chars: int = 12000
    default_max_new_tokens: int = 128
    default_min_new_tokens: int = 32

    # FastAPI (optional)
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
