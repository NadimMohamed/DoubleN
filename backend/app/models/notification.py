from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum
from app.db.session import Base

class NotificationType(PyEnum):
    PRICE_ALERT = "price_alert"
    TREND_ALERT = "trend_alert"
    SIGNAL_ALERT = "signal_alert"
    POSITION_ALERT = "position_alert"
    MARGIN_ALERT = "margin_alert"
    DISCONNECTION_ALERT = "disconnection_alert"
    ERROR_ALERT = "error_alert"
    INFO = "info"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(
        postgresql.ENUM(
            'price_alert',
            'trend_alert',
            'signal_alert',
            'position_alert',
            'margin_alert',
            'disconnection_alert',
            'error_alert',
            'info',
            name='notificationtype',
            create_type=False,
        ),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    symbol = Column(String(20), nullable=True, index=True)
    data = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="notifications")
