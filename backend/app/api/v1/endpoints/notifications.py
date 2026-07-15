from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_user, get_db
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationMarkAsRead,
    NotificationClearRequest,
)
from app.services.notification import notification_service
from app.models.user import User
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a notification for the current user."""
    return await notification_service.create_notification(db, current_user.id, notification_data)

@router.get("", response_model=dict)
async def get_notifications(
    unread_only: bool = False,
    symbol: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notifications for the current user."""
    notifications, total = await notification_service.get_notifications(
        db, current_user.id, unread_only, symbol, limit, offset
    )
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count,
        "limit": limit,
        "offset": offset,
    }

@router.post("/mark-as-read")
async def mark_as_read(
    data: NotificationMarkAsRead,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark notifications as read."""
    count = await notification_service.mark_as_read(db, current_user.id, data.notification_ids)
    return {"marked_as_read": count}

@router.post("/clear")
async def clear_old_notifications(
    request: NotificationClearRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear old read notifications."""
    count = await notification_service.clear_old_notifications(
        db, current_user.id, request.older_than_days or 30
    )
    return {"cleared": count}

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}
