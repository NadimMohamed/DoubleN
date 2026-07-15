from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db
from app.services.binance import binance_client
import json
import structlog

log = structlog.get_logger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, symbol: str, websocket: WebSocket):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)
        log.info("ws.connected", symbol=symbol)
    
    def disconnect(self, symbol: str, websocket: WebSocket):
        self.active_connections[symbol].remove(websocket)
        if not self.active_connections[symbol]:
            del self.active_connections[symbol]
        log.info("ws.disconnected", symbol=symbol)
    
    async def broadcast(self, symbol: str, data: dict):
        if symbol in self.active_connections:
            disconnected = []
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(data)
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect(symbol, conn)

manager = ConnectionManager()

@router.websocket("/ws/market/{symbol}")
async def websocket_market_endpoint(websocket: WebSocket, symbol: str):
    symbol = symbol.upper()
    await manager.connect(symbol, websocket)
    
    try:
        while True:
            # Receive ping/keepalive from client
            data = await websocket.receive_text()
            
            # Get latest ticker
            ticker = await binance_client.get_ticker_24h(symbol)
            
            # Broadcast to all clients listening to this symbol
            await manager.broadcast(symbol, {
                "type": "ticker",
                "symbol": symbol,
                "price": ticker.price,
                "price_change_pct": ticker.price_change_pct,
                "high_24h": ticker.high_24h,
                "low_24h": ticker.low_24h,
                "volume": ticker.volume,
                "timestamp": ticker.last_updated
            })
    
    except WebSocketDisconnect:
        manager.disconnect(symbol, websocket)
        log.info("ws.client_disconnected", symbol=symbol)
    except Exception as e:
        manager.disconnect(symbol, websocket)
        log.error("ws.error", symbol=symbol, error=str(e))
