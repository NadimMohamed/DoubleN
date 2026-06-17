import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.schemas.market import TickerPrice
from datetime import datetime, timezone


def make_ticker(symbol: str) -> TickerPrice:
    return TickerPrice(
        symbol=symbol,
        price=50000.0,
        price_change=1000.0,
        price_change_pct=2.0,
        high_24h=51000.0,
        low_24h=49000.0,
        volume=1234.5,
        quote_volume=61725000.0,
        open_price=49000.0,
        last_updated=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
class TestWatchlist:
    async def test_get_empty_watchlist(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/v1/watchlist", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_add_symbol(self, client: AsyncClient, auth_headers):
        with patch(
            "app.api.v1.endpoints.watchlist.binance_client.get_multiple_tickers",
            new_callable=AsyncMock,
            return_value=[make_ticker("BTCUSDT")],
        ):
            resp = await client.post(
                "/api/v1/watchlist",
                json={"symbol": "BTCUSDT"},
                headers=auth_headers,
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["symbol"] == "BTCUSDT"
        assert data["base_asset"] == "BTC"
        assert data["quote_asset"] == "USDT"
        assert "id" in data

    async def test_add_duplicate_symbol(self, client: AsyncClient, auth_headers):
        # First add
        await client.post("/api/v1/watchlist", json={"symbol": "ETHUSDT"}, headers=auth_headers)
        # Second add — should 409
        resp = await client.post("/api/v1/watchlist", json={"symbol": "ETHUSDT"}, headers=auth_headers)
        assert resp.status_code == 409

    async def test_add_unsupported_symbol(self, client: AsyncClient, auth_headers):
        resp = await client.post(
            "/api/v1/watchlist",
            json={"symbol": "FAKECOIN"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_get_watchlist_with_prices(self, client: AsyncClient, auth_headers):
        # Add a symbol first
        add_resp = await client.post(
            "/api/v1/watchlist",
            json={"symbol": "SOLUSDT"},
            headers=auth_headers,
        )
        assert add_resp.status_code == 201

        # Fetch with mocked prices
        with patch(
            "app.api.v1.endpoints.watchlist.binance_client.get_multiple_tickers",
            new_callable=AsyncMock,
            return_value=[make_ticker("SOLUSDT")],
        ):
            resp = await client.get("/api/v1/watchlist", headers=auth_headers)

        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["symbol"] == "SOLUSDT"
        assert items[0]["price"] == 50000.0
        assert items[0]["price_change_pct_24h"] == 2.0

    async def test_remove_symbol(self, client: AsyncClient, auth_headers):
        # Add
        add_resp = await client.post(
            "/api/v1/watchlist",
            json={"symbol": "ADAUSDT"},
            headers=auth_headers,
        )
        assert add_resp.status_code == 201
        item_id = add_resp.json()["id"]

        # Remove
        del_resp = await client.delete(f"/api/v1/watchlist/{item_id}", headers=auth_headers)
        assert del_resp.status_code == 204

        # Verify gone
        with patch(
            "app.api.v1.endpoints.watchlist.binance_client.get_multiple_tickers",
            new_callable=AsyncMock,
            return_value=[],
        ):
            list_resp = await client.get("/api/v1/watchlist", headers=auth_headers)
        assert list_resp.json() == []

    async def test_remove_nonexistent_item(self, client: AsyncClient, auth_headers):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await client.delete(f"/api/v1/watchlist/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404

    async def test_watchlist_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/watchlist")
        assert resp.status_code == 403

    async def test_add_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/v1/watchlist", json={"symbol": "BTCUSDT"})
        assert resp.status_code == 403
