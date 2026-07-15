from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PositionCreate(BaseModel):
    symbol: str
    side: str
    quantity: float
    entry_price: float
    leverage: float = 1.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PositionUpdate(BaseModel):
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PositionResponse(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    leverage: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    status: str
    opened_at: datetime
    closed_at: Optional[datetime]

    model_config = {"from_attributes": True}

class PositionCloseRequest(BaseModel):
    exit_price: float
