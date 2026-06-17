"""
WebSocket manager.
Connects to Binance WebSocket streams and broadcasts real-time
price updates to all subscribed frontend clients.

Binance stream docs: https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams
"""
import asyncio
import json
import websockets
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import structlog

from app.core.config import settings

log = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages frontend WebSocket connections per symbol."""

    def __init__(self):
        # symbol → set of connected WebSocket clients
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, ws: WebSocket, symbol: str):
        await ws.accept()
        symbol = symbol.upper()
        if symbol not in self._connections:
            self._connections[symbol] = set()
        self._connections[symbol].add(ws)
        log.info("ws.client.connected", symbol=symbol, total=len(self._connections[symbol]))

    def disconnect(self, ws: WebSocket, symbol: str):
        symbol = symbol.upper()
        if symbol in self._connections:
            self._connections[symbol].discard(ws)
            log.info("ws.client.disconnected", symbol=symbol)

    async def broadcast(self, symbol: str, data: dict):
        symbol = symbol.upper()
        clients = self._connections.get(symbol, set()).copy()
        if not clients:
            return

        dead = set()
        for ws in clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self._connections[symbol].discard(ws)

    def get_subscribed_symbols(self) -> Set[str]:
        return {s for s, conns in self._connections.items() if conns}


manager = ConnectionManager()


async def binance_stream_worker(symbol: str):
    """
    Maintains a persistent connection to the Binance miniTicker stream
    for `symbol` and broadcasts updates to all connected clients.

    Binance stream: wss://stream.binance.com:9443/ws/{symbol}@miniTicker
    Message format:
    {
      "e": "24hrMiniTicker",
      "E": 1672515782136,
      "s": "BTCUSDT",
      "c": "16999.00",   ← current/last price
      "o": "16000.00",   ← open
      "h": "17100.00",   ← high
      "l": "15900.00",   ← low
      "v": "123.456",    ← base volume
      "q": "1234567.89"  ← quote volume
    }
    """
    stream_url = f"{settings.BINANCE_WS_URL}/ws/{symbol.lower()}@miniTicker"
    backoff = 1

    while True:
        try:
            log.info("binance.stream.connecting", symbol=symbol, url=stream_url)
            async with websockets.connect(
                stream_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5,
            ) as ws:
                backoff = 1  # reset on successful connection
                log.info("binance.stream.connected", symbol=symbol)

                async for raw_message in ws:
                    try:
                        data = json.loads(raw_message)
                        payload = {
                            "type": "ticker",
                            "symbol": data["s"],
                            "price": float(data["c"]),
                            "open": float(data["o"]),
                            "high": float(data["h"]),
                            "low": float(data["l"]),
                            "volume": float(data["v"]),
                            "quote_volume": float(data["q"]),
                            "timestamp": data["E"],
                        }
                        await manager.broadcast(symbol, payload)
                    except (KeyError, ValueError, json.JSONDecodeError) as e:
                        log.warning("binance.stream.parse_error", error=str(e))

        except (websockets.exceptions.ConnectionClosed,
                websockets.exceptions.WebSocketException,
                ConnectionError, OSError) as e:
            log.warning(
                "binance.stream.disconnected",
                symbol=symbol,
                error=str(e),
                reconnect_in=backoff,
            )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)  # exponential backoff, cap at 60s

        except asyncio.CancelledError:
            log.info("binance.stream.cancelled", symbol=symbol)
            break
        except Exception as e:
            log.error("binance.stream.error", symbol=symbol, error=str(e))
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)
