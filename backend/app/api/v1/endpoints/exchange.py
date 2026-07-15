from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.exchange import ExchangeAccount, Position
from app.services.bingx import BingXClient
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/exchange", tags=["exchange"])

@router.get("/account")
async def get_exchange_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get connected exchange account balance"""
    # TODO: Get stored API keys from database
    # For now, return placeholder
    return {
        "exchange": "bingx",
        "status": "not_connected",
        "message": "Please connect your BingX account in settings"
    }

@router.get("/positions")
async def get_positions(
    current_user: User = Depends(get_current_user),
):
    """Get all open trading positions"""
    return {
        "positions": [],
        "total_pnl": 0.0,
        "total_pnl_percentage": 0.0
    }

@router.post("/connect")
async def connect_exchange(
    api_key: str,
    api_secret: str,
    current_user: User = Depends(get_current_user),
):
    """Connect to BingX exchange"""
    # TODO: Validate and store API keys securely
    return {"status": "connected", "message": "Exchange connected"}
