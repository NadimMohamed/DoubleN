"""
Binance REST API client.
All price data comes directly from https://api.binance.com
No mocks, no fake data.
"""
import httpx
from datetime import datetime, timezone
from typing import Optional
import structlog
from app.core.config import settings
from app.schemas.market import TickerPrice, KlineData, OrderBook, OrderBookEntry

log = structlog.get_logger(__name__)

BINANCE_BASE = settings.BINANCE_BASE_URL


class BinanceClient:
    """Async HTTP client for Binance public market data endpoints."""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=BINANCE_BASE,
                timeout=httpx.Timeout(10.0, connect=5.0),
                headers={"User-Agent": "DoubleNTrading/1.0"},
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def ping(self) -> bool:
        """Check Binance API connectivity."""
        try:
            client = await self._get_client()
            r = await client.get("/api/v3/ping")
            return r.status_code == 200
        except Exception as e:
            log.error("binance.ping.failed", error=str(e))
            return False

    async def get_ticker_24h(self, symbol: str) -> TickerPrice:
        """
        GET /api/v3/ticker/24hr
        Returns 24h rolling window price statistics for a symbol.
        """
        client = await self._get_client()
        r = await client.get("/api/v3/ticker/24hr", params={"symbol": symbol.upper()})
        r.raise_for_status()
        d = r.json()
        return TickerPrice(
            symbol=d["symbol"],
            price=float(d["lastPrice"]),
            price_change=float(d["priceChange"]),
            price_change_pct=float(d["priceChangePercent"]),
            high_24h=float(d["highPrice"]),
            low_24h=float(d["lowPrice"]),
            volume=float(d["volume"]),
            quote_volume=float(d["quoteVolume"]),
            open_price=float(d["openPrice"]),
            last_updated=datetime.now(timezone.utc),
        )

    async def get_multiple_tickers(self, symbols: list[str]) -> list[TickerPrice]:
        """
        Batch fetch multiple tickers in a single API call.
        GET /api/v3/ticker/24hr with no symbol returns all tickers.
        We filter to the requested symbols.
        """
        if not symbols:
            return []

        client = await self._get_client()
        # Use the batch endpoint — more efficient than N individual calls
        import json as _json
        symbols_upper = [s.upper() for s in symbols]
        params = {"symbols": _json.dumps(symbols_upper)}
        r = await client.get("/api/v3/ticker/24hr", params=params)
        r.raise_for_status()

        results = []
        for d in r.json():
            results.append(TickerPrice(
                symbol=d["symbol"],
                price=float(d["lastPrice"]),
                price_change=float(d["priceChange"]),
                price_change_pct=float(d["priceChangePercent"]),
                high_24h=float(d["highPrice"]),
                low_24h=float(d["lowPrice"]),
                volume=float(d["volume"]),
                quote_volume=float(d["quoteVolume"]),
                open_price=float(d["openPrice"]),
                last_updated=datetime.now(timezone.utc),
            ))
        return results

    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 200,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> list[KlineData]:
        """
        GET /api/v3/klines
        Returns OHLCV candlestick data for TradingView charts.
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h,
                   1d, 3d, 1w, 1M
        """
        client = await self._get_client()
        params: dict = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        r = await client.get("/api/v3/klines", params=params)
        r.raise_for_status()

        candles = []
        for row in r.json():
            candles.append(KlineData(
                open_time=row[0],
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                close_time=row[6],
                quote_volume=float(row[7]),
                num_trades=row[8],
            ))
        return candles

    async def get_order_book(self, symbol: str, limit: int = 20) -> OrderBook:
        """
        GET /api/v3/depth
        Returns current order book bids/asks.
        """
        client = await self._get_client()
        r = await client.get("/api/v3/depth", params={"symbol": symbol.upper(), "limit": limit})
        r.raise_for_status()
        d = r.json()
        return OrderBook(
            symbol=symbol.upper(),
            last_update_id=d["lastUpdateId"],
            bids=[OrderBookEntry(price=float(b[0]), quantity=float(b[1])) for b in d["bids"]],
            asks=[OrderBookEntry(price=float(a[0]), quantity=float(a[1])) for a in d["asks"]],
        )

    async def get_exchange_info(self, symbol: Optional[str] = None) -> dict:
        """GET /api/v3/exchangeInfo — symbol metadata."""
        client = await self._get_client()
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        r = await client.get("/api/v3/exchangeInfo", params=params)
        r.raise_for_status()
        return r.json()


# Module-level singleton — reused across requests
binance_client = BinanceClient()
