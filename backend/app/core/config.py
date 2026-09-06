import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "SentinelAI")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    postgres_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/sentinelaidb")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    env: str = os.getenv("ENV", "development")
    redis_rate_limit_window_seconds: int = int(os.getenv("REDIS_RATE_LIMIT_WINDOW_SECONDS", 60))
    redis_rate_limit_max_requests: int = int(os.getenv("REDIS_RATE_LIMIT_MAX_REQUESTS", 10))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_timeout_seconds: int = int(os.getenv("OPENAI_TIMEOUT_SECONDS", 30))
    openai_retry_count: int = int(os.getenv("OPENAI_RETRY_COUNT", 1))

    def __init__(self) -> None:
        if not self.postgres_url.startswith("postgresql+psycopg://"):
            raise RuntimeError("DATABASE_URL must use the PostgreSQL psycopg URL format")

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
