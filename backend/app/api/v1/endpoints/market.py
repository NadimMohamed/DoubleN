from fastapi import APIRouter, HTTPException, Query, Path
from typing import Literal
import structlog

from app.services.binance import binance_client
from app.schemas.market import TickerPrice, KlineData, OrderBook, SUPPORTED_SYMBOLS

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/market", tags=["market"])

VALID_INTERVALS = {"1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w","1M"}


def _validate_symbol(symbol: str) -> str:
    s = symbol.upper()
    if s not in SUPPORTED_SYMBOLS:
        raise HTTPException(
            status_code=400,
            detail=f"Symbol {s} not supported. Supported: {sorted(SUPPORTED_SYMBOLS)}",
        )
    return s


@router.get(
    "/ticker/{symbol}",
    response_model=TickerPrice,
    summary="Get live 24h ticker for a symbol (from Binance)",
)
async def get_ticker(symbol: str = Path(..., description="e.g. BTCUSDT")):
    symbol = _validate_symbol(symbol)
    try:
        return await binance_client.get_ticker_24h(symbol)
    except Exception as e:
        log.warning(
            "market.ticker.fallback_to_mock",
            symbol=symbol,
            error=str(e),
            msg="Binance API unavailable, falling back to mock ticker data",
        )
        return binance_client.get_mock_ticker(symbol)


@router.get(
    "/tickers",
    response_model=list[TickerPrice],
    summary="Get live tickers for multiple symbols",
)
async def get_tickers(
    symbols: str = Query(
        default="BTCUSDT,ETHUSDT,LTCUSDT,SOLUSDT",
        description="Comma-separated symbols",
    )
):
    syms = [_validate_symbol(s.strip()) for s in symbols.split(",") if s.strip()]
    if not syms:
        raise HTTPException(status_code=400, detail="No valid symbols provided")
    try:
        return await binance_client.get_multiple_tickers(syms)
    except Exception as e:
        log.warning(
            "market.tickers.fallback_to_mock",
            symbols=syms,
            error=str(e),
            msg="Binance API unavailable, falling back to mock ticker data",
        )
        return binance_client.get_mock_tickers(syms)


@router.get(
    "/klines/{symbol}",
    response_model=list[KlineData],
    summary="Get OHLCV candlestick data (for TradingView charts)",
)
async def get_klines(
    symbol: str = Path(...),
    interval: str = Query(default="1h", description="Candle interval"),
    limit: int = Query(default=200, ge=1, le=1000),
):
    symbol = _validate_symbol(symbol)
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Valid: {VALID_INTERVALS}")
    try:
        return await binance_client.get_klines(symbol, interval, limit)
    except Exception as e:
        log.warning(
            "market.klines.fallback_to_mock",
            symbol=symbol,
            error=str(e),
            msg="Binance API unavailable, falling back to mock kline data",
        )
        return binance_client.get_mock_klines(symbol, interval, limit)


@router.get(
    "/orderbook/{symbol}",
    response_model=OrderBook,
    summary="Get current order book",
)
async def get_order_book(
    symbol: str = Path(...),
    limit: int = Query(default=20, ge=5, le=100),
):
    symbol = _validate_symbol(symbol)
    try:
        return await binance_client.get_order_book(symbol, limit)
    except Exception as e:
        log.warning(
            "market.orderbook.fallback_to_mock",
            symbol=symbol,
            error=str(e),
            msg="Binance API unavailable, falling back to mock order book data",
        )
        return binance_client.get_mock_order_book(symbol, limit)


@router.get(
    "/symbols",
    summary="List all supported trading symbols",
)
async def get_supported_symbols():
    return {"symbols": sorted(SUPPORTED_SYMBOLS)}
