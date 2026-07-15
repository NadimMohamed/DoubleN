from typing import Set
from fastapi import WebSocket
import structlog

log = structlog.get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        log.info("ws.connected", symbol=symbol, total_connections=len(self.active_connections[symbol]))

    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
        log.info("ws.disconnected", symbol=symbol)

    async def broadcast(self, symbol: str, data: dict):
        if symbol in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    log.warning("ws.send_failed", symbol=symbol, error=str(e))
                    disconnected.add(connection)
            
            for connection in disconnected:
                self.disconnect(connection, symbol)

manager = ConnectionManager()
