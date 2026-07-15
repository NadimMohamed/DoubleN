from typing import Set, Dict
from fastapi import WebSocket, WebSocketDisconnect, status
import structlog
import json
from datetime import datetime

log = structlog.get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, Set[WebSocket]] = {}
        self.authenticated_users: dict[WebSocket, str] = {}  # ws -> user_id mapping

    async def connect(self, websocket: WebSocket, symbol: str, user_id: str = None):
        """Connect a websocket, optionally tracking authenticated user."""
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        
        if user_id:
            self.authenticated_users[websocket] = user_id
        
        log.info(
            "ws.connected",
            symbol=symbol,
            user_id=user_id,
            total_connections=len(self.active_connections[symbol])
        )

    def disconnect(self, websocket: WebSocket, symbol: str):
        """Disconnect a websocket."""
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
        
        # Clean up user mapping
        if websocket in self.authenticated_users:
            user_id = self.authenticated_users.pop(websocket)
            log.info("ws.disconnected", symbol=symbol, user_id=user_id)
        else:
            log.info("ws.disconnected", symbol=symbol)

    async def broadcast(self, symbol: str, data: dict):
        """Broadcast to all connected clients for a symbol."""
        if symbol not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[symbol]:
            try:
                await connection.send_json(data)
            except Exception as e:
                log.warning("ws.send_failed", symbol=symbol, error=str(e))
                disconnected.add(connection)
        
        for connection in disconnected:
            self.disconnect(connection, symbol)

    async def send_to_user(self, user_id: str, symbol: str, data: dict):
        """Send data only to authenticated user's connections."""
        if symbol not in self.active_connections:
            return
        
        for connection in self.active_connections[symbol]:
            if self.authenticated_users.get(connection) == user_id:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    log.warning("ws.user_send_failed", user_id=user_id, error=str(e))

    def get_user_connections(self, user_id: str, symbol: str) -> Set[WebSocket]:
        """Get all connections for a specific user on a symbol."""
        if symbol not in self.active_connections:
            return set()
        
        return {
            conn for conn in self.active_connections[symbol]
            if self.authenticated_users.get(conn) == user_id
        }

manager = ConnectionManager()
