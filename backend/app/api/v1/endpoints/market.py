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
    summary="Get live 24h ticker for a symbol (from Binance)",
)
async def get_ticker(response: Response, symbol: str = Path(..., description="e.g. BTCUSDT")):
    symbol = _validate_symbol(symbol)
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    try:
        return await binance_client.get_ticker_24h(symbol)
    except Exception as e:
        log.warning(
            "market.ticker.fallback_to_mock",
            symbol=symbol,
            error=str(e),
            msg="Binance API unavailable, falling back to mock ticker data",
        )
        try:
            return binance_client.get_mock_ticker(symbol)
        except Exception as mock_err:
            log.error("market.ticker.mock_failed", symbol=symbol, error=str(mock_err))
            raise HTTPException(status_code=502, detail="Unable to retrieve ticker data") from mock_err


@router.get(
    "/tickers",
    response_model=list[TickerPrice],
    summary="Get live tickers for multiple symbols",
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
    try:
        return await binance_client.get_multiple_tickers(syms)
    except Exception as e:
        log.warning(
            "market.tickers.fallback_to_mock",
            symbols=syms,
            error=str(e),
            msg="Binance API unavailable, falling back to mock ticker data",
        )
        try:
            return binance_client.get_mock_tickers(syms)
        except Exception as mock_err:
            log.error("market.tickers.mock_failed", symbols=syms, error=str(mock_err))
            raise HTTPException(status_code=502, detail="Unable to retrieve ticker data") from mock_err


@router.get(
    "/klines/{symbol}",
    response_model=list[KlineData],
    summary="Get OHLCV candlestick data (for TradingView charts)",
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
    try:
        return await binance_client.get_klines(symbol, interval, limit)
    except Exception as e:
        log.warning(
            "market.klines.fallback_to_mock",
            symbol=symbol,
            interval=interval,
            limit=limit,
            error=str(e),
            msg="Binance API unavailable, falling back to mock kline data",
        )
        try:
            return binance_client.get_mock_klines(symbol, interval, limit)
        except Exception as mock_err:
            log.error("market.klines.mock_failed", symbol=symbol, error=str(mock_err))
            raise HTTPException(status_code=502, detail="Unable to retrieve kline data") from mock_err


@router.get(
    "/orderbook/{symbol}",
    response_model=OrderBook,
    summary="Get current order book",
)
async def get_order_book(
    response: Response,
    symbol: str = Path(...),
    limit: int = Query(default=20, ge=5, le=100),
):
    symbol = _validate_symbol(symbol)
    response.headers["Cache-Control"] = CACHE_CONTROL_SHORT
    try:
        return await binance_client.get_order_book(symbol, limit)
    except Exception as e:
        log.warning(
            "market.orderbook.fallback_to_mock",
            symbol=symbol,
            limit=limit,
            error=str(e),
            msg="Binance API unavailable, falling back to mock order book data",
        )
        try:
            return binance_client.get_mock_order_book(symbol, limit)
        except Exception as mock_err:
            log.error("market.orderbook.mock_failed", symbol=symbol, error=str(mock_err))
            raise HTTPException(status_code=502, detail="Unable to retrieve order book data") from mock_err


@router.get(
    "/symbols",
    summary="List all supported trading symbols",
)
async def get_supported_symbols(response: Response):
    response.headers["Cache-Control"] = CACHE_CONTROL_SYMBOLS
    return {"symbols": sorted(SUPPORTED_SYMBOLS)}
