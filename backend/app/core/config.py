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
        default=["*"],
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

    # ── Data Sources ─────────────────────────────────────────────────────────
    # Binance's REST/WebSocket endpoints are frequently unreachable from
    # Railway's hosting IPs (HTTP 451 — geo-blocked). When enabled, ticker
    # requests fall back to CoinGecko's free public API (real data, no auth
    # required, 10-50 calls/minute — sufficient for polling dashboards).
    # Priority order: binance > coingecko. This app never falls back to
    # simulated/mock data — if both real sources fail, an error is returned.
    USE_COINGECKO_FALLBACK: bool = True
    COINGECKO_API_TIMEOUT: int = 10

    # Simulated/mock market data is disabled by default and should only ever
    # be re-enabled explicitly, as a deliberate emergency override — never as
    # a silent fallback. When False (the default), no endpoint will return
    # fabricated prices under any circumstance.
    USE_MOCK_DATA: bool = False

    # When True (the default), the app requires real data from Binance or
    # CoinGecko for every market data request. If both fail, the request
    # fails with a 503 rather than silently degrading to stale/fake data.
    REQUIRE_LIVE_DATA: bool = True

    # ── Rate limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
