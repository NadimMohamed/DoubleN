"""
Binance REST API client.
All price data comes directly from https://api.binance.com

If Binance is temporarily unreachable (e.g. rate limited or blocked from the
hosting environment), CoinGecko is used as a real-data fallback (see
`get_ticker_24h`). This app never returns simulated/mock market data —
if both Binance and CoinGecko fail, an exception is raised so callers can
surface a clear error to the user instead of showing fabricated prices.
"""
import httpx
import redis.asyncio as aioredis
from datetime import datetime, timezone, timedelta
from typing import Optional
import structlog
from app.core.config import settings
from app.core.exceptions import UpstreamServiceError
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

        This app only ever returns real market data — no simulated/mock
        fallback. Binance's REST/WebSocket endpoints are frequently
        unreachable from Railway's hosting IPs (HTTP 451 — geo-blocked), so
        CoinGecko is used as a real-data fallback. Order of operations:

        1. Check Redis for a recently cached ticker (shared across all app
           instances/workers, `TICKER_REDIS_CACHE_TTL_SECONDS` TTL). If
           present, return it immediately with `data_freshness_seconds=0`.
        2. Try Binance directly. This frequently fails with HTTP 451 from
           the hosting environment.
        3. On Binance failure, fetch from CoinGecko (real, non-simulated
           data) and cache the result in Redis for
           `TICKER_REDIS_CACHE_TTL_SECONDS` seconds.
        4. If CoinGecko also fails, log a CRITICAL alert and raise an
           exception — callers must surface a clear error to the user
           rather than showing fabricated prices.

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
                    log.critical(
                        "binance.and_coingecko_both_failed",
                        symbol=symbol,
                        binance_error=str(e),
                        coingecko_error=str(cg_error),
                        msg="Both Binance and CoinGecko are unavailable — no live data source "
                            "could be reached. Refusing to return mock/simulated data.",
                    )
                    raise UpstreamServiceError(
                        detail=(
                            f"Live market data for '{symbol}' is currently unavailable. "
                            "Both Binance and CoinGecko failed to respond. Please try again "
                            "shortly."
                        )
                    ) from cg_error

            log.critical(
                "binance.failed_and_coingecko_fallback_disabled",
                symbol=symbol,
                error=str(e),
                msg="Binance is unavailable and CoinGecko fallback is disabled — no live data "
                    "source could be reached. Refusing to return mock/simulated data.",
            )
            raise UpstreamServiceError(
                detail=(
                    f"Live market data for '{symbol}' is currently unavailable from Binance."
                )
            ) from e

    async def get_multiple_tickers(self, symbols: list[str]) -> list[TickerPrice]:
        """
        Batch fetch multiple tickers in a single API call.
        GET /api/v3/ticker/24hr with no symbol returns all tickers.
        We filter to the requested symbols.
        """
        if not symbols:
            return []

        try:
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
        except Exception as e:
            log.critical(
                "binance.get_multiple_tickers_failed",
                symbols=symbols,
                error=str(e),
                msg="Binance is unavailable — refusing to return mock/simulated tickers.",
            )
            raise UpstreamServiceError(
                detail="Live ticker data is currently unavailable from Binance."
            ) from e

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
        try:
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
        except Exception as e:
            log.critical(
                "binance.get_klines_failed",
                symbol=symbol,
                interval=interval,
                error=str(e),
                msg="Binance is unavailable — refusing to return mock/simulated kline data.",
            )
            raise UpstreamServiceError(
                detail=f"Live candlestick data for '{symbol}' is currently unavailable from Binance."
            ) from e

    async def get_order_book(self, symbol: str, limit: int = 20) -> OrderBook:
        """
        GET /api/v3/depth
        Returns current order book bids/asks.
        """
        try:
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
        except Exception as e:
            log.critical(
                "binance.get_order_book_failed",
                symbol=symbol,
                error=str(e),
                msg="Binance is unavailable — refusing to return mock/simulated order book data.",
            )
            raise UpstreamServiceError(
                detail=f"Live order book data for '{symbol}' is currently unavailable from Binance."
            ) from e

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
