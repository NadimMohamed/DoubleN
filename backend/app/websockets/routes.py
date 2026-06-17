from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websockets.manager import manager
from app.schemas.market import SUPPORTED_SYMBOLS
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/ticker/{symbol}")
async def websocket_ticker(
    websocket: WebSocket,
    symbol: str,
    token: str = Query(default=None, description="Optional JWT for auth"),
):
    """
    WebSocket endpoint for live price streaming.

    Connect: ws://host/ws/ticker/BTCUSDT

    Receives messages:
    {
        "type": "ticker",
        "symbol": "BTCUSDT",
        "price": 67432.10,
        "open": 66000.00,
        "high": 68100.00,
        "low": 65800.00,
        "volume": 18432.5,
        "quote_volume": 1234567890.0,
        "timestamp": 1716000000000
    }
    """
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        await websocket.close(code=4004, reason=f"Symbol {symbol} not supported")
        return

    await manager.connect(websocket, symbol)
    try:
        # Keep connection alive; client can send pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
    except Exception as e:
        log.error("ws.ticker.error", symbol=symbol, error=str(e))
        manager.disconnect(websocket, symbol)
