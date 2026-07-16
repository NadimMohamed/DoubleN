from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.services.position_service import PositionService
from app.schemas.position import PositionCreate, PositionResponse, PositionCloseRequest
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/trading/positions", tags=["positions"])

@router.post("", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    data: PositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Open a new trading position"""
    return await PositionService.create_position(db, current_user.id, data)

@router.get("", response_model=list[PositionResponse])
async def list_open_positions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all open positions for current user"""
    return await PositionService.get_open_positions(db, current_user.id)

@router.post("/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id: str,
    request: PositionCloseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Close an open position"""
    return await PositionService.close_position(db, position_id, request.exit_price)

@router.patch("/{position_id}", response_model=PositionResponse)
async def update_position_price(
    position_id: str,
    current_price: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update position current price and PnL"""
    return await PositionService.update_position_price(db, position_id, current_price)
