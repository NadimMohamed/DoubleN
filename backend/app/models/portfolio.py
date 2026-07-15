from sqlalchemy import String, Float, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.session import Base

class Position(Base):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=True)
    take_profit: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Position {self.symbol} {self.quantity}@{self.entry_price}>"

    @property
    def pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity

    @property
    def pnl_percentage(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

    @property
    def value(self) -> float:
        return self.current_price * self.quantity

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY or SELL
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=True)
    pnl: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Trade {self.side} {self.symbol} {self.quantity}@{self.entry_price}>"

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PRICE_ALERT, SIGNAL_ALERT, etc
    target_price: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    triggered: Mapped[bool] = mapped_column(default=False)
    triggered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Alert {self.alert_type} {self.symbol}@{self.target_price}>"
