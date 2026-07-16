from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum, Integer
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(Enum(PositionSide), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    leverage = Column(Float, default=1.0)

    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)

    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_pct = Column(Float, default=0.0)
    realized_pnl = Column(Float, nullable=True)

    status = Column(Enum(PositionStatus), default=PositionStatus.OPEN, index=True)
    opened_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="positions")
