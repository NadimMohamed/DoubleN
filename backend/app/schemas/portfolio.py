from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PositionCreate(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PositionResponse(PositionCreate):
    id: str
    user_id: str
    pnl: float
    pnl_percentage: float
    value: float
    created_at: datetime

class TradeCreate(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None

class TradeResponse(TradeCreate):
    id: str
    user_id: str
    pnl: Optional[float] = None
    status: str
    created_at: datetime
    closed_at: Optional[datetime] = None

class AlertCreate(BaseModel):
    symbol: str
    alert_type: str
    target_price: Optional[float] = None

class AlertResponse(AlertCreate):
    id: str
    user_id: str
    is_active: bool
    triggered: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime

class PortfolioSummary(BaseModel):
    total_balance: float
    total_invested: float
    unrealized_pnl: float
    realized_pnl: float
    pnl_percentage: float
    positions_count: int
    open_trades_count: int
    closed_trades_count: int
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
