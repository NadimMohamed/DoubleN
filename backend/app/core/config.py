from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from typing import List
import secrets


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "Double N Trading"
    APP_ENV: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(64)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/double_n_trading"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "double_n_trading"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    # ── Redis ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ─────────────────────────────────────────────────────────────────
    FRONTEND_URL: str = Field(
        default="https://dn-frontend-production-43b8.up.railway.app",
        description="Frontend URL for CORS configuration"
    )
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://dn-frontend-production-43b8.up.railway.app"

    # Allowed hosts for TrustedHostMiddleware
    ALLOWED_HOSTS: list = Field(
        default=["doublen-production.up.railway.app", "localhost", "127.0.0.1"],
        description="Allowed hosts list"
    )

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── Binance ──────────────────────────────────────────────────────────────
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_BASE_URL: str = "https://api.binance.com"
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443"

    # ── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
