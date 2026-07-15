from typing import Optional, List
from enum import Enum
import statistics
import structlog
from app.schemas.market import KlineData

log = structlog.get_logger(__name__)

class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class TrendAnalysis:
    @staticmethod
    def detect_trend(klines: List[KlineData]) -> tuple:
        """Detect trend using moving average crossover (10 vs 20)."""
        if len(klines) < 20:
            return TrendDirection.NEUTRAL, 0.0
        
        closes = [float(k.close) for k in klines]
        ma10 = statistics.mean(closes[-10:])
        ma20 = statistics.mean(closes[-20:])
        
        if ma10 > ma20:
            direction = TrendDirection.BULLISH
            strength = min(100, ((ma10 - ma20) / ma20) * 1000)
        elif ma10 < ma20:
            direction = TrendDirection.BEARISH
            strength = min(100, ((ma20 - ma10) / ma20) * 1000)
        else:
            direction = TrendDirection.NEUTRAL
            strength = 0.0
        
        return direction, strength

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(klines: List[KlineData], period: int = 14) -> Optional[float]:
        """Calculate RSI indicator (0-100, >70 overbought, <30 oversold)."""
        if len(klines) < period:
            return None
        
        closes = [float(k.close) for k in klines[-period-1:]]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [d for d in deltas if d > 0]
        losses = [abs(d) for d in deltas if d < 0]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

class SupportResistance:
    @staticmethod
    def calculate_levels(klines: List[KlineData], period: int = 20) -> dict:
        """Calculate support, resistance, and pivot levels."""
        if len(klines) < period:
            return {"support": None, "resistance": None, "pivot": None}
        
        recent = klines[-period:]
        highs = [float(k.high) for k in recent]
        lows = [float(k.low) for k in recent]
        
        support = min(lows)
        resistance = max(highs)
        pivot = (resistance + support) / 2
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "pivot": round(pivot, 2),
        }

class SignalGenerator:
    @staticmethod
    def generate_signal(trend, rsi: Optional[float], current_price: float, sr: dict) -> tuple:
        """Generate trading signal with confidence score."""
        points = 0
        max_points = 0
        reasons = []
        
        # Trend component
        max_points += 40
        if trend == TrendDirection.BULLISH:
            points += 40
            reasons.append("Bullish trend")
        elif trend == TrendDirection.BEARISH:
            reasons.append("Bearish trend")
        
        # RSI component
        if rsi is not None:
            max_points += 40
            if rsi < 30:
                points += 40
                reasons.append("RSI oversold")
            elif rsi > 70:
                reasons.append("RSI overbought")
            else:
                points += 20
        
        # Support/Resistance
        max_points += 20
        if sr["support"] and current_price < sr["support"] * 1.05:
            points += 20
            reasons.append("Near support")
        
        confidence = (points / max_points) * 100 if max_points > 0 else 0
        
        if confidence >= 65:
            signal = SignalType.BUY if trend == TrendDirection.BULLISH else SignalType.SELL
        elif confidence <= 35:
            signal = SignalType.SELL if trend == TrendDirection.BULLISH else SignalType.BUY
        else:
            signal = SignalType.HOLD
        
        return signal, round(confidence, 1), "; ".join(reasons)

class RiskManagement:
    @staticmethod
    def calculate_stop_loss(entry_price: float, percentage: float = 2.0) -> float:
        """Calculate stop loss price."""
        return round(entry_price * (1 - percentage / 100), 2)
    
    @staticmethod
    def calculate_take_profit(entry_price: float, multiplier: float = 2.0) -> float:
        """Calculate take profit price (as % above entry)."""
        return round(entry_price * (1 + multiplier / 100), 2)
    
    @staticmethod
    def calculate_position_size(balance: float, entry: float, stop_loss: float, risk_pct: float = 2.0) -> dict:
        """Calculate position size based on risk management."""
        risk_amount = balance * (risk_pct / 100)
        price_diff = abs(entry - stop_loss)
        
        if price_diff == 0:
            return {"position_size": None, "risk_amount": None}
        
        position = risk_amount / price_diff
        return {
            "position_size": round(position, 4),
            "risk_amount": round(risk_amount, 2),
        }
