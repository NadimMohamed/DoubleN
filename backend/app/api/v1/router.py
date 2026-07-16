from fastapi import APIRouter
from app.api.v1.endpoints import auth, market, watchlist, trading
from app.api.v1.endpoints import notifications
from app.api.v1.endpoints import analysis
from app.api.v1.endpoints import exchange
from app.api.v1.endpoints import positions
from app.api.v1 import websocket

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(market.router)
api_router.include_router(watchlist.router)
api_router.include_router(trading.router)
api_router.include_router(notifications.router)
api_router.include_router(analysis.router)
api_router.include_router(exchange.router)
api_router.include_router(positions.router)
api_router.include_router(websocket.router)
