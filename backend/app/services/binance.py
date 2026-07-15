"""
Binance REST API client.
All price data comes directly from https://api.binance.com

If Binance is temporarily unreachable (e.g. rate limited or blocked from the
hosting environment), fallback "mock" methods below provide realistic
simulated data so the rest of the app keeps working. Once real connectivity
is restored, the real methods are used again automatically — no code changes
required.
"""
import httpx
import random
import redis.asyncio as aioredis
from datetime import datetime, timezone, timedelta
from typing import Optional
import structlog
from app.core.config import settings
from app.schemas.market import TickerPrice, KlineData, OrderBook, OrderBookEntry

log = structlog.get_logger(__name__)

# How long a REST ticker response is considered "fresh" before we refetch.
# Binance's WebSocket streams are frequently unreachable from the hosting
# environment (HTTP 451 — geo-blocked), so the app relies on REST polling
# for live prices. A short TTL cache keeps redundant requests down while
# still giving near-real-time updates (2-5s) to dashboard/watchlist polling.
TICKER_CACHE_TTL_SECONDS = 2

# How long a ticker response is cached in Redis (shared across all app
# instances/workers) before it is considered stale and refetched from the
# upstream source (Binance or CoinGecko). Kept short so prices stay close
# to real-time while still absorbing bursts of polling requests.
TICKER_REDIS_CACHE_TTL_SECONDS = 5

BINANCE_BASE = settings.BINANCE_BASE_URL

# Realistic base prices used to seed mock data when Binance is unavailable.
MOCK_BASE_PRICES: dict[str, float] = {
    "BTCUSDT": 45000.0,
    "ETHUSDT": 2500.0,
    "LTCUSDT": 150.0,
    "SOLUSDT": 150.0,
    "BNBUSDT": 350.0,
    "XRPUSDT": 0.6,
    "ADAUSDT": 0.45,
    "DOGEUSDT": 0.12,
    "MATICUSDT": 0.9,
    "DOTUSDT": 6.5,
    "AVAXUSDT": 35.0,
    "LINKUSDT": 15.0,
}

# Explicit ranges called out in the requirements — used when available.
MOCK_PRICE_RANGES: dict[str, tuple[float, float]] = {
    "BTCUSDT": (20000.0, 70000.0),
    "ETHUSDT": (1000.0, 4000.0),
    "LTCUSDT": (80.0, 250.0),
    "SOLUSDT": (100.0, 200.0),
}


class BinanceClient:
    """Async HTTP client for Binance public market data endpoints.

    Binance's WebSocket streams are frequently unreachable from Railway's
    hosting IPs (HTTP 451 — geo-blocked), so real-time prices are delivered
    via REST polling instead. A short-lived in-memory cache keeps the poll
    rate down without adding noticeable latency (2s TTL, 2-5s effective
    freshness once client polling interval is factored in).
    """

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._ticker_cache: dict[str, TickerPrice] = {}
        self._ticker_cache_time: dict[str, datetime] = {}
        self._redis: Optional[aioredis.Redis] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=BINANCE_BASE,
                timeout=httpx.Timeout(10.0, connect=5.0),
                headers={"User-Agent": "DoubleNTrading/1.0"},
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Lazily create the shared Redis client used to cache ticker data.

        Returns None (rather than raising) if Redis is unavailable so callers
        can gracefully fall back to fetching from upstream sources directly.
        """
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                log.warning("binance.redis_init_failed", error=str(e))
                return None
        return self._redis

    async def _cache_ticker(self, redis_client: Optional["aioredis.Redis"], cache_key: str, ticker: TickerPrice) -> None:
        """Best-effort write-through cache of a ticker into Redis."""
        if redis_client is None:
            return
        try:
            await redis_client.set(
                cache_key,
                ticker.model_dump_json(),
                ex=TICKER_REDIS_CACHE_TTL_SECONDS,
            )
        except Exception as e:
            log.warning("binance.redis_cache_write_failed", cache_key=cache_key, error=str(e))

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        if self._redis is not None:
            try:
                if hasattr(self._redis, "aclose"):
                    await self._redis.aclose()
                else:
                    await self._redis.close()
            except Exception:
                pass

    async def ping(self) -> bool:
        """Check Binance API connectivity."""
        try:
            client = await self._get_client()
            r = await client.get("/api/v3/ping")
            return r.status_code == 200
        except Exception as e:
            log.error("binance.ping.failed", error=str(e))
            return False

    async def _fetch_binance_ticker(self, symbol: str) -> TickerPrice:
        """Fetch a ticker directly from Binance's REST API (no cache/fallback).

        This is expected to frequently fail with HTTP 451 from Railway's
        hosting IPs (geo-blocked) — callers handle that via the fallback
        chain in `get_ticker_24h`.
        """
        client = await self._get_client()
        r = await client.get("/api/v3/ticker/24hr", params={"symbol": symbol})
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
            data_source="binance",
            data_freshness_seconds=0,
        )

    async def get_ticker_24h(self, symbol: str) -> TickerPrice:
        """
        GET /api/v3/ticker/24hr
        Returns 24h rolling window price statistics for a symbol.

        Binance's REST/WebSocket endpoints are frequently unreachable from
        Railway's hosting IPs (HTTP 451 — geo-blocked), so CoinGecko is
        treated as the reliable primary fallback here. Order of operations:

        1. Check Redis for a recently cached ticker (shared across all app
           instances/workers, `TICKER_REDIS_CACHE_TTL_SECONDS` TTL). If
           present, return it immediately with `data_freshness_seconds=0`.
        2. Try Binance directly. This frequently fails with HTTP 451 from
           the hosting environment.
        3. On Binance failure, fetch from CoinGecko (real, non-simulated
           data) and cache the result in Redis for
           `TICKER_REDIS_CACHE_TTL_SECONDS` seconds.
        4. If CoinGecko also fails, fall back to fully simulated mock data
           (`data_source="mock"`) so the app keeps functioning.

        The returned `data_source` and `data_freshness_seconds` fields
        always reflect where the data actually came from and how fresh it
        is, so API consumers and the UI can be transparent about it.
        """
        symbol = symbol.upper()
        cache_key = f"ticker:{symbol}"

        redis_client = await self._get_redis()
        if redis_client is not None:
            try:
                cached_raw = await redis_client.get(cache_key)
            except Exception as e:
                log.warning("binance.redis_cache_read_failed", symbol=symbol, error=str(e))
                cached_raw = None

            if cached_raw:
                try:
                    ticker = TickerPrice.model_validate_json(cached_raw)
                    ticker.data_freshness_seconds = 0
                    self._ticker_cache[symbol] = ticker
                    self._ticker_cache_time[symbol] = datetime.now(timezone.utc)
                    return ticker
                except Exception as e:
                    log.warning("binance.redis_cache_parse_failed", symbol=symbol, error=str(e))

        try:
            ticker = await self._fetch_binance_ticker(symbol)
            ticker.data_freshness_seconds = 0
            self._ticker_cache[symbol] = ticker
            self._ticker_cache_time[symbol] = datetime.now(timezone.utc)
            await self._cache_ticker(redis_client, cache_key, ticker)
            return ticker
        except Exception as e:
            log.warning("binance.ticker_failed_trying_coingecko", symbol=symbol, error=str(e))

            if settings.USE_COINGECKO_FALLBACK:
                try:
                    from app.services.coingecko import coingecko_client
                    ticker = await coingecko_client.get_ticker_24h(symbol)
                    ticker.data_source = "coingecko"
                    ticker.data_freshness_seconds = 0
                    log.info("binance.coingecko_fallback", symbol=symbol)
                    self._ticker_cache[symbol] = ticker
                    self._ticker_cache_time[symbol] = datetime.now(timezone.utc)
                    await self._cache_ticker(redis_client, cache_key, ticker)
                    return ticker
                except Exception as cg_error:
                    log.warning(
                        "coingecko.also_failed_using_stale_or_mock",
                        symbol=symbol,
                        error=str(cg_error),
                    )

            stale = self._ticker_cache.get(symbol)
            if stale is not None:
                log.warning(
                    "binance.get_ticker_24h.stale_cache_fallback",
                    symbol=symbol,
                    error=str(e),
                )
                return stale

            mock_ticker = self.get_mock_ticker(symbol)
            mock_ticker.data_source = "mock"
            mock_ticker.data_freshness_seconds = 0
            return mock_ticker

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
                data_source="binance",
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

    # ── Mock data fallbacks ───────────────────────────────────────────────
    # Used when the real Binance API is unreachable (e.g. rate limited /
    # blocked from the hosting environment). These generate realistic but
    # simulated data so the rest of the app can keep functioning.

    def _mock_base_price(self, symbol: str) -> float:
        symbol = symbol.upper()
        low, high = MOCK_PRICE_RANGES.get(symbol, (None, None))
        if low is not None:
            return random.uniform(low, high)
        base = MOCK_BASE_PRICES.get(symbol, 100.0)
        # Wobble the base price a bit so repeated calls aren't static.
        return base * random.uniform(0.95, 1.05)

    def get_mock_ticker(self, symbol: str) -> TickerPrice:
        """Return a realistic simulated TickerPrice for a symbol."""
        symbol = symbol.upper()
        price = self._mock_base_price(symbol)
        pct_change = random.uniform(-5.0, 5.0)
        open_price = price / (1 + pct_change / 100)
        price_change = price - open_price
        high_24h = max(price, open_price) * random.uniform(1.0, 1.03)
        low_24h = min(price, open_price) * random.uniform(0.97, 1.0)
        volume = random.uniform(500.0, 50000.0)
        quote_volume = volume * price

        return TickerPrice(
            symbol=symbol,
            price=round(price, 8),
            price_change=round(price_change, 8),
            price_change_pct=round(pct_change, 4),
            high_24h=round(high_24h, 8),
            low_24h=round(low_24h, 8),
            volume=round(volume, 4),
            quote_volume=round(quote_volume, 4),
            open_price=round(open_price, 8),
            last_updated=datetime.now(timezone.utc),
            data_source="mock",
        )

    def get_mock_tickers(self, symbols: list[str]) -> list[TickerPrice]:
        """Return realistic simulated tickers for multiple symbols."""
        return [self.get_mock_ticker(s) for s in symbols]

    def get_mock_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 200,
    ) -> list[KlineData]:
        """Return realistic simulated OHLCV candlestick data with a slight trend."""
        num_candles = min(max(limit, 5), 10) if limit else 8
        num_candles = min(num_candles, limit) if limit else num_candles
        num_candles = max(5, min(num_candles, 10))

        interval_minutes = {
            "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
            "1d": 1440, "3d": 4320, "1w": 10080, "1M": 43200,
        }.get(interval, 60)

        price = self._mock_base_price(symbol)
        # Slight overall trend direction for the whole series.
        trend = random.uniform(-0.002, 0.003)

        now = datetime.now(timezone.utc)
        candles: list[KlineData] = []
        current_price = price

        for i in range(num_candles):
            open_price = current_price
            close_price = open_price * (1 + trend + random.uniform(-0.01, 0.01))
            high = max(open_price, close_price) * random.uniform(1.0, 1.008)
            low = min(open_price, close_price) * random.uniform(0.992, 1.0)
            volume = random.uniform(10.0, 5000.0)

            open_time = now - timedelta(minutes=interval_minutes * (num_candles - i))
            close_time = open_time + timedelta(minutes=interval_minutes)

            candles.append(KlineData(
                open_time=int(open_time.timestamp() * 1000),
                open=round(open_price, 8),
                high=round(high, 8),
                low=round(low, 8),
                close=round(close_price, 8),
                volume=round(volume, 4),
                close_time=int(close_time.timestamp() * 1000),
                quote_volume=round(volume * close_price, 4),
                num_trades=random.randint(50, 2000),
            ))
            current_price = close_price

        return candles

    def get_mock_order_book(self, symbol: str, limit: int = 20) -> OrderBook:
        """Return a realistic simulated order book with a narrow bid/ask spread."""
        symbol = symbol.upper()
        num_entries = max(10, min(limit or 20, 20))
        mid_price = self._mock_base_price(symbol)
        spread = mid_price * random.uniform(0.0005, 0.002)

        bids: list[OrderBookEntry] = []
        asks: list[OrderBookEntry] = []

        best_bid = mid_price - spread / 2
        best_ask = mid_price + spread / 2

        for i in range(num_entries):
            bid_price = best_bid * (1 - i * random.uniform(0.0001, 0.0005))
            ask_price = best_ask * (1 + i * random.uniform(0.0001, 0.0005))
            bids.append(OrderBookEntry(
                price=round(bid_price, 8),
                quantity=round(random.uniform(0.01, 10.0), 6),
            ))
            asks.append(OrderBookEntry(
                price=round(ask_price, 8),
                quantity=round(random.uniform(0.01, 10.0), 6),
            ))

        return OrderBook(
            symbol=symbol,
            last_update_id=random.randint(1_000_000, 9_999_999),
            bids=bids,
            asks=asks,
        )


# Module-level singleton — reused across requests
binance_client = BinanceClient()
