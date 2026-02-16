from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database (SQLite for development, PostgreSQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./autobuzz.db"
    DATABASE_URL_SYNC: str = "sqlite:///./autobuzz.db"

    # Redis (optional for dev)
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # OpenAI
    OPENAI_API_KEY: str = ""

    # X (Twitter) API
    X_API_KEY: str = ""
    X_API_SECRET: str = ""
    X_BEARER_TOKEN: str = ""

    # Threads API
    THREADS_APP_ID: str = ""
    THREADS_APP_SECRET: str = ""

    # News API
    NEWS_API_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # App
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
