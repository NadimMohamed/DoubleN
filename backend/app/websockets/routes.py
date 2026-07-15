from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Path, Query
import asyncio
import structlog
from app.websockets.manager import manager
from app.services.binance import binance_client
from app.schemas.market import SUPPORTED_SYMBOLS
from app.core.exceptions import InvalidSymbolError

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

async def _validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValueError("Symbol must not be empty")
    s = symbol.strip().upper()
    if s not in SUPPORTED_SYMBOLS:
        raise InvalidSymbolError(s, SUPPORTED_SYMBOLS)
    return s

@router.websocket("/ticker/{symbol}")
async def websocket_ticker(
    websocket: WebSocket,
    symbol: str = Path(...),
    token: str = Query(..., description="JWT access token"),
    update_interval: int = Query(default=5, ge=1, le=60),
):
    """
    WebSocket endpoint for live ticker streaming.
    
    Requires authentication via JWT token in query parameter.
    Connect with: ws://host/ws/ticker/BTCUSDT?token=YOUR_JWT_TOKEN
    """
    try:
        symbol = await _validate_symbol(symbol)
    except (ValueError, InvalidSymbolError) as e:
        await websocket.close(code=1008, reason=str(e))
        return
    
    # Authenticate user via JWT token
    try:
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token: no user")
            return
        log.info("ws.authenticated", symbol=symbol, user_id=user_id)
    except Exception as e:
        log.warning("ws.auth_failed", symbol=symbol, error=str(e))
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await manager.connect(websocket, symbol, user_id=user_id)
    try:
        while True:
            try:
                ticker = await binance_client.get_ticker_24h(symbol)
                data = {
                    "symbol": ticker.symbol,
                    "price": ticker.price,
                    "price_change": ticker.price_change,
                    "price_change_pct": ticker.price_change_pct,
                    "high_24h": ticker.high_24h,
                    "low_24h": ticker.low_24h,
                    "volume": ticker.volume,
                    "quote_volume": ticker.quote_volume,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await manager.broadcast(symbol, data)
            except Exception as e:
                log.warning("ws.ticker_fetch_failed", symbol=symbol, error=str(e))
                try:
                    ticker = binance_client.get_mock_ticker(symbol)
                    data = {
                        "symbol": ticker.symbol,
                        "price": ticker.price,
                        "price_change": ticker.price_change,
                        "price_change_pct": ticker.price_change_pct,
                        "high_24h": ticker.high_24h,
                        "low_24h": ticker.low_24h,
                        "volume": ticker.volume,
                        "quote_volume": ticker.quote_volume,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    await manager.broadcast(symbol, data)
                except Exception as mock_err:
                    log.error("ws.mock_ticker_failed", symbol=symbol, error=str(mock_err))

            await asyncio.sleep(update_interval)

    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
        log.info("ws.disconnect", symbol=symbol, user_id=user_id)
    except Exception as e:
        log.error("ws.error", symbol=symbol, error=str(e))
        manager.disconnect(websocket, symbol)
