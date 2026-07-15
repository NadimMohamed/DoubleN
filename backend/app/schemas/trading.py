from pydantic import BaseModel
from typing import Optional
from enum import Enum


class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Signal(BaseModel):
    signal: SignalType
    confidence: float
    reasoning: str


class Trend(BaseModel):
    direction: TrendDirection
    strength: float


class SupportResistance(BaseModel):
    support: Optional[float]
    resistance: Optional[float]


class Indicators(BaseModel):
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    ema_12: Optional[float]
    ema_26: Optional[float]
    atr: Optional[float]


class MarketAnalysis(BaseModel):
    symbol: str
    current_price: float
    signal: Signal
    trend: Trend
    support_resistance: SupportResistance
    indicators: Indicators


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
