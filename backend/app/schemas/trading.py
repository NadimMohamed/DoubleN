from pydantic import BaseModel, Field
from typing import Optional

class TrendResponse(BaseModel):
    direction: str
    strength: float

class SupportResistanceResponse(BaseModel):
    support: Optional[float] = None
    resistance: Optional[float] = None
    pivot: Optional[float] = None

class IndicatorResponse(BaseModel):
    rsi: Optional[float] = None

class SignalResponse(BaseModel):
    signal: str
    confidence: float
    reasoning: str

class RiskManagementResponse(BaseModel):
    entry_price: float
    stop_loss: float
    take_profit_2x: float
    take_profit_3x: float
    position_size: Optional[float] = None
    risk_amount: Optional[float] = None

class TradeAnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    trend: TrendResponse
    support_resistance: SupportResistanceResponse
    indicators: IndicatorResponse
    signal: SignalResponse
    risk_management: RiskManagementResponse
    timestamp: str
