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
    X_ACCESS_TOKEN: str = ""
    X_ACCESS_TOKEN_SECRET: str = ""

    # Threads API
    THREADS_APP_ID: str = ""
    THREADS_APP_SECRET: str = ""
    THREADS_ACCESS_TOKEN: str = ""

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
        try:
            parsed = json.loads(self.CORS_ORIGINS)
            if isinstance(parsed, list):
                return parsed
            # JSON formatted but not a list? wrap it
            return [str(parsed)]
        except json.JSONDecodeError:
            # Fallback for plain string (single URL or comma-separated)
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Render等のPaaSが提供する postgres:// を postgresql:// に置換
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        # Async用のドライバ指定がない場合、PostgreSQLなら +asyncpg を付与
        if self.DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in self.DATABASE_URL:
            self.DATABASE_URL_SYNC = self.DATABASE_URL  # Sync用はそのまま
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif self.DATABASE_URL.startswith("sqlite"):
            # SQLiteの場合はそのまま (dev env)
            pass
        
        # デプロイ環境でDATABASE_URL_SYNCがセットされていない場合の補完
        if not self.DATABASE_URL_SYNC and self.DATABASE_URL.startswith("postgresql+asyncpg://"):
             self.DATABASE_URL_SYNC = self.DATABASE_URL.replace("+asyncpg", "")



settings = Settings()
