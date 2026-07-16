from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum
from app.db.session import Base

class PositionSide(str, PyEnum):
    LONG = "long"
    SHORT = "short"

class PositionStatus(str, PyEnum):
    OPEN = "open"
    CLOSED = "closed"

class Position(Base):
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(postgresql.ENUM('long', 'short', name='positionside', create_type=False), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    leverage = Column(Float, default=1.0)

    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_pct = Column(Float, default=0.0)
    realized_pnl = Column(Float, nullable=True)

    status = Column(postgresql.ENUM('open', 'closed', name='positionstatus', create_type=False), default=PositionStatus.OPEN, index=True)
    opened_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="positions")
