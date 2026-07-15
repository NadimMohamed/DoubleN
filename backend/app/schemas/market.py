from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Literal
from datetime import datetime
import uuid


# ── Watchlist ─────────────────────────────────────────────────────────────────
SUPPORTED_SYMBOLS = {
    "BTCUSDT", "ETHUSDT", "LTCUSDT", "SOLUSDT",
    "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT",
    "MATICUSDT", "DOTUSDT", "AVAXUSDT", "LINKUSDT",
}


class WatchlistAdd(BaseModel):
    symbol: str

    @field_validator("symbol")
    @classmethod
    def symbol_upper(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in SUPPORTED_SYMBOLS:
            raise ValueError(f"Symbol {v} not supported. Supported: {sorted(SUPPORTED_SYMBOLS)}")
        return v


class WatchlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    symbol: str
    base_asset: str
    quote_asset: str
    added_at: datetime


class WatchlistWithPrice(BaseModel):
    id: uuid.UUID
    symbol: str
    base_asset: str
    quote_asset: str
    added_at: datetime
    # Live data from Binance (None if fetch fails)
    price: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_pct_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    quote_volume_24h: Optional[float] = None


# ── Ticker / Market data ──────────────────────────────────────────────────────
class TickerPrice(BaseModel):
    symbol: str
    price: float
    price_change: float
    price_change_pct: float
    high_24h: float
    low_24h: float
    volume: float
    quote_volume: float
    open_price: float
    last_updated: datetime

    # Tracks where this data actually came from so API consumers and the UI
    # can be transparent about it — Binance is frequently geo-blocked (HTTP
    # 451) from Railway's hosting IPs, so responses may fall back to
    # CoinGecko (real data, alternative source).
    data_source: Literal["binance", "coingecko"] = "binance"

    # Richer market data (populated when available, e.g. from CoinGecko).
    market_cap: Optional[float] = None
    market_cap_change_pct: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    ath: Optional[float] = None
    atl: Optional[float] = None

    # How many seconds old this data is relative to when it was fetched from
    # the upstream source. 0 means it was just fetched (or served from a
    # very short-lived cache); higher values indicate staler data.
    data_freshness_seconds: Optional[int] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "BTCUSDT",
                "price": 45000.0,
                "price_change": 500.0,
                "price_change_pct": 1.12,
                "high_24h": 45800.0,
                "low_24h": 44200.0,
                "volume": 12345.6789,
                "quote_volume": 555555555.55,
                "open_price": 44500.0,
                "last_updated": "2024-01-01T00:00:00Z",
                "data_source": "binance",
            }
        }
    )


class OrderBookEntry(BaseModel):
    price: float
    quantity: float


class OrderBook(BaseModel):
    symbol: str
    bids: list[OrderBookEntry]
    asks: list[OrderBookEntry]
    last_update_id: int


class KlineData(BaseModel):
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    quote_volume: float
    num_trades: int
