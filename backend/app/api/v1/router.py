from fastapi import APIRouter
from app.api.v1.endpoints import auth, market, watchlist

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(market.router)
api_router.include_router(watchlist.router)
