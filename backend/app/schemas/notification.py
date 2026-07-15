from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class NotificationType(str, Enum):
    PRICE_ALERT = "price_alert"
    TREND_ALERT = "trend_alert"
    SIGNAL_ALERT = "signal_alert"
    POSITION_ALERT = "position_alert"
    MARGIN_ALERT = "margin_alert"
    DISCONNECTION_ALERT = "disconnection_alert"
    ERROR_ALERT = "error_alert"
    INFO = "info"

class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    message: str
    symbol: Optional[str] = None
    data: Optional[dict] = None

class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    symbol: Optional[str] = None
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class NotificationMarkAsRead(BaseModel):
    notification_ids: list[str]

class NotificationClearRequest(BaseModel):
    older_than_days: Optional[int] = 30
