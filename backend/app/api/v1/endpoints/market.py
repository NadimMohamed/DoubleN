from fastapi import APIRouter, HTTPException, Query, Path, Response
from typing import Literal
import structlog

from app.services.binance import binance_client
from app.schemas.market import TickerPrice, KlineData, OrderBook, SUPPORTED_SYMBOLS
from app.core.exceptions import InvalidSymbolError, ValidationError

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/market", tags=["market"])

VALID_INTERVALS = {"1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w","1M"}

# How long clients/CDNs may cache market data responses. These endpoints
# reflect near-real-time data so we keep this short.
CACHE_CONTROL_SHORT = "public, max-age=5"
CACHE_CONTROL_SYMBOLS = "public, max-age=3600"


def _validate_symbol(symbol: str) -> str:
    """Normalize and validate a symbol against the supported set.

    Raises InvalidSymbolError (400) instead of allowing an unsupported
    symbol to reach Binance and produce a confusing upstream error.
    """
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol must not be empty")
    s = symbol.strip().upper()
    if s not in SUPPORTED_SYMBOLS:
        raise InvalidSymbolError(s, SUPPORTED_SYMBOLS)
    return s


@router.get(
    "/ticker/{symbol}",
    response_model=TickerPrice,
    summary="Get 24h ticker (from Binance or CoinGecko — live data only)",
    description=(
        "Returns ticker data from Binance if available, falling back to "
        "CoinGecko when Binance is unreachable (e.g. geo-blocked from the "
        "hosting environment). This endpoint never returns simulated/mock "
        "data — if both Binance and CoinGecko are unavailable, a 503 error "
        "is returned instead of fabricated prices. Check the 'data_source' "
        "field on the response to see which origin actually served the data."
    ),
)
async def get_ticker(response: Response, symbol: str = Path(..., description="e.g. BTCUSDT")):
    symbol = _validate_symbol(symbol)
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    return await binance_client.get_ticker_24h(symbol)


@router.get(
    "/tickers",
    response_model=list[TickerPrice],
    summary="Get tickers for multiple symbols (from Binance or CoinGecko — live data only)",
    description=(
        "Returns ticker data from Binance if available, falling back to "
        "CoinGecko per-symbol. This endpoint never returns simulated/mock "
        "data — if a symbol cannot be served from either source, the "
        "request fails with an error rather than showing fabricated prices. "
        "Check each item's 'data_source' field to see which origin served "
        "that entry."
    ),
)
async def get_tickers(
    response: Response,
    symbols: str = Query(
        default="BTCUSDT,ETHUSDT,LTCUSDT,SOLUSDT",
        description="Comma-separated symbols",
    ),
):
    syms = [_validate_symbol(s) for s in symbols.split(",") if s.strip()]
    if not syms:
        raise ValidationError("No valid symbols provided")
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    return await binance_client.get_multiple_tickers(syms)


@router.get(
    "/klines/{symbol}",
    response_model=list[KlineData],
    summary="Get OHLCV candlestick data (for TradingView charts) — live data only",
)
async def get_klines(
    response: Response,
    symbol: str = Path(...),
    interval: str = Query(default="1h", description="Candle interval"),
    limit: int = Query(default=200, ge=1, le=1000),
):
    symbol = _validate_symbol(symbol)
    if interval not in VALID_INTERVALS:
        raise ValidationError(f"Invalid interval '{interval}'. Valid: {sorted(VALID_INTERVALS)}")
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    return await binance_client.get_klines(symbol, interval, limit)


@router.get(
    "/orderbook/{symbol}",
    response_model=OrderBook,
    summary="Get current order book — live data only",
)
async def get_order_book(
    response: Response,
    symbol: str = Path(...),
    limit: int = Query(default=20, ge=5, le=100),
):
    symbol = _validate_symbol(symbol)
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    return await binance_client.get_order_book(symbol, limit)


@router.get(
    "/symbols",
    summary="List all supported trading symbols",
)
async def get_supported_symbols(response: Response):
    response.headers["Cache-Control"] = CACHE_CONTROL_SYMBOLS
    return {"symbols": sorted(SUPPORTED_SYMBOLS)}
