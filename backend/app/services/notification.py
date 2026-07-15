from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse
import structlog

log = structlog.get_logger(__name__)

class NotificationService:
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: str,
        notification_data: NotificationCreate,
        expires_in_hours: Optional[int] = 24,
    ) -> NotificationResponse:
        """Create a new notification for a user."""
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        notification = Notification(
            user_id=user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            symbol=notification_data.symbol,
            data=notification_data.data,
            expires_at=expires_at,
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        log.info("notification.created", user_id=user_id, notification_id=notification.id)
        return NotificationResponse.model_validate(notification)
    
    @staticmethod
    async def get_notifications(
        db: AsyncSession,
        user_id: str,
        unread_only: bool = False,
        symbol: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[NotificationResponse], int]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        if symbol:
            query = query.where(Notification.symbol == symbol.upper())
        
        # Exclude expired notifications
        now = datetime.now(timezone.utc)
        query = query.where(
            (Notification.expires_at == None) | (Notification.expires_at > now)
        )
        
        # Count total
        count_result = await db.execute(select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            (Notification.expires_at == None) | (Notification.expires_at > now)
        ))
        total = count_result.scalar() or 0
        
        # Get paginated results (newest first)
        query = query.order_by(desc(Notification.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return (
            [NotificationResponse.model_validate(n) for n in notifications],
            total,
        )
    
    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        user_id: str,
        notification_ids: list[str],
    ) -> int:
        """Mark notifications as read."""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.id.in_(notification_ids),
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            count += 1
        
        await db.commit()
        log.info("notifications.marked_read", user_id=user_id, count=count)
        return count
    
    @staticmethod
    async def clear_old_notifications(
        db: AsyncSession,
        user_id: str,
        older_than_days: int = 30,
    ) -> int:
        """Delete old read notifications."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == True,
                Notification.created_at < cutoff_date,
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        count = len(notifications)
        for notification in notifications:
            await db.delete(notification)
        
        await db.commit()
        log.info("notifications.cleared", user_id=user_id, count=count)
        return count
    
    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: str) -> int:
        """Get count of unread notifications."""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        result = await db.execute(query)
        notifications = result.scalars().all()
        return len(notifications)

notification_service = NotificationService()
