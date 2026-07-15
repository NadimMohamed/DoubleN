from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class ExchangeAccount(BaseModel):
    """Exchange account information"""
    total_balance: float
    available_balance: float
    locked_balance: float
    currency: str = "USDT"

class Position(BaseModel):
    """Trading position"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    leverage: float
    liquidation_price: Optional[float] = None

class ExchangeConnection(BaseModel):
    """Exchange API connection"""
    exchange: str  # "bingx"
    is_connected: bool
    last_connected: Optional[str] = None
    account_balance: Optional[float] = None
