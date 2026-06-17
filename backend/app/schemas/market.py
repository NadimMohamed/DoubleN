from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
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
