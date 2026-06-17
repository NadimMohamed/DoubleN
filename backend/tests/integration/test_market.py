import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import datetime, timezone

from app.schemas.market import TickerPrice, KlineData, OrderBook, OrderBookEntry


def make_ticker(symbol="BTCUSDT") -> TickerPrice:
    return TickerPrice(
        symbol=symbol, price=67000.0, price_change=500.0,
        price_change_pct=0.75, high_24h=68000.0, low_24h=66000.0,
        volume=12345.0, quote_volume=823_000_000.0, open_price=66500.0,
        last_updated=datetime.now(timezone.utc),
    )


def make_kline() -> KlineData:
    return KlineData(
        open_time=1716000000000, open=66000.0, high=67500.0,
        low=65800.0, close=67000.0, volume=100.0,
        close_time=1716003600000, quote_volume=6_700_000.0, num_trades=5000,
    )


@pytest.mark.asyncio
class TestMarketEndpoints:
    async def test_get_ticker(self, client: AsyncClient):
        with patch(
            "app.api.v1.endpoints.market.binance_client.get_ticker_24h",
            new_callable=AsyncMock,
            return_value=make_ticker("BTCUSDT"),
        ):
            resp = await client.get("/api/v1/market/ticker/BTCUSDT")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "BTCUSDT"
        assert data["price"] == 67000.0

    async def test_get_ticker_lowercase_normalised(self, client: AsyncClient):
        with patch(
            "app.api.v1.endpoints.market.binance_client.get_ticker_24h",
            new_callable=AsyncMock,
            return_value=make_ticker("ETHUSDT"),
        ):
            resp = await client.get("/api/v1/market/ticker/ethusdt")
        assert resp.status_code == 200

    async def test_get_ticker_unsupported_symbol(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/ticker/FAKECOIN")
        assert resp.status_code == 400

    async def test_get_tickers_multiple(self, client: AsyncClient):
        with patch(
            "app.api.v1.endpoints.market.binance_client.get_multiple_tickers",
            new_callable=AsyncMock,
            return_value=[make_ticker("BTCUSDT"), make_ticker("ETHUSDT")],
        ):
            resp = await client.get(
                "/api/v1/market/tickers",
                params={"symbols": "BTCUSDT,ETHUSDT"},
            )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_klines(self, client: AsyncClient):
        with patch(
            "app.api.v1.endpoints.market.binance_client.get_klines",
            new_callable=AsyncMock,
            return_value=[make_kline() for _ in range(100)],
        ):
            resp = await client.get("/api/v1/market/klines/BTCUSDT", params={"interval": "1h"})
        assert resp.status_code == 200
        assert len(resp.json()) == 100

    async def test_get_klines_invalid_interval(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/klines/BTCUSDT", params={"interval": "5years"})
        assert resp.status_code == 400

    async def test_get_supported_symbols(self, client: AsyncClient):
        resp = await client.get("/api/v1/market/symbols")
        assert resp.status_code == 200
        data = resp.json()
        assert "symbols" in data
        assert "BTCUSDT" in data["symbols"]
        assert "ETHUSDT" in data["symbols"]

    async def test_health_endpoint(self, client: AsyncClient):
        with patch(
            "app.main.binance_client.ping",
            new_callable=AsyncMock,
            return_value=True,
        ):
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
