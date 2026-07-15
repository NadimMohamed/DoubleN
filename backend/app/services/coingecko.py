"""
CoinGecko REST API client — fallback market data source.

Binance's REST/WebSocket endpoints are frequently unreachable from Railway's
hosting IPs (HTTP 451 — geo-blocked). When that happens, this client provides
real (non-simulated) market data pulled from CoinGecko's free public API
(no auth required, 10-50 calls/minute rate limit — sufficient for
polling-based dashboards updating every 10-30 seconds).

Data returned here is real market data, but note it is a different source
than Binance (different aggregation methodology, slightly different prices).
Callers should tag responses with `data_source="coingecko"` so the origin is
transparent to API consumers and the UI.
"""
import httpx
import structlog
from datetime import datetime, timezone
from typing import Optional
from app.schemas.market import TickerPrice, KlineData
from app.core.config import settings

log = structlog.get_logger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Map symbol names to CoinGecko IDs
SYMBOL_TO_COINGECKO = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "LTCUSDT": "litecoin",
    "SOLUSDT": "solana",
    "BNBUSDT": "binancecoin",
    "XRPUSDT": "ripple",
    "ADAUSDT": "cardano",
    "DOGEUSDT": "dogecoin",
    "MATICUSDT": "matic-network",
    "DOTUSDT": "polkadot",
    "AVAXUSDT": "avalanche-2",
    "LINKUSDT": "chainlink",
}


class CoinGeckoClient:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=COINGECKO_BASE,
                timeout=httpx.Timeout(
                    float(settings.COINGECKO_API_TIMEOUT), connect=5.0
                ),
                headers={"User-Agent": "DoubleNTrading/1.0"},
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    def _symbol_to_id(symbol: str) -> Optional[str]:
        """Convert symbol like BTCUSDT to coingecko ID like bitcoin."""
        return SYMBOL_TO_COINGECKO.get(symbol.upper())

    async def get_ticker_24h(self, symbol: str) -> TickerPrice:
        """Fetch 24h ticker data from CoinGecko."""
        cg_id = self._symbol_to_id(symbol)
        if not cg_id:
            raise ValueError(f"Symbol {symbol} not supported on CoinGecko")

        try:
            client = await self._get_client()
            r = await client.get(
                "/simple/price",
                params={
                    "ids": cg_id,
                    "vs_currency": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_high_low_24h": "true",
                }
            )
            r.raise_for_status()
            data = r.json()

            if not data or cg_id not in data:
                raise ValueError(f"No data returned for {symbol}")

            coin_data = data[cg_id]
            price = coin_data.get("usd", 0)
            change_24h = coin_data.get("usd_24h_change", 0)
            high_24h = coin_data.get("usd_24h_high", price)
            low_24h = coin_data.get("usd_24h_low", price)
            volume = coin_data.get("usd_24h_vol", 0)

            return TickerPrice(
                symbol=symbol.upper(),
                price=float(price),
                price_change=float(price * change_24h / 100),
                price_change_pct=float(change_24h),
                high_24h=float(high_24h),
                low_24h=float(low_24h),
                volume=float(volume) if volume else 0,
                quote_volume=float(volume) if volume else 0,
                open_price=float(price / (1 + change_24h / 100)),
                last_updated=datetime.now(timezone.utc),
                data_source="coingecko",
            )

        except Exception as e:
            log.error("coingecko.ticker_failed", symbol=symbol, error=str(e))
            raise


# Module-level singleton
coingecko_client = CoinGeckoClient()
