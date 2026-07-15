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

    @staticmethod
    def calculate_macd(klines: List[KlineData], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        Returns MACD, signal line, and histogram.
        """
        if len(klines) < slow:
            return {"macd": None, "signal": None, "histogram": None}
        
        closes = [float(k.close) for k in klines]
        
        # Simple EMA approximation
        def ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return statistics.mean(data) if data else 0
            multiplier = 2 / (period + 1)
            ema_val = statistics.mean(data[:period])
            for price in data[period:]:
                ema_val = price * multiplier + ema_val * (1 - multiplier)
            return ema_val
        
        ema12 = ema(closes, fast)
        ema26 = ema(closes, slow)
        macd_line = ema12 - ema26
        
        # Signal line is EMA of MACD
        macd_values = []
        for i in range(slow, len(closes)):
            ema12 = ema(closes[:i+1], fast)
            ema26 = ema(closes[:i+1], slow)
            macd_values.append(ema12 - ema26)
        
        signal_line = ema(macd_values, signal) if macd_values else macd_line
        histogram = macd_line - signal_line
        
        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(histogram, 4),
            "interpretation": "bullish" if histogram > 0 else "bearish"
        }

    @staticmethod
    def calculate_bollinger_bands(klines: List[KlineData], period: int = 20, std_dev_multiplier: float = 2.0) -> dict:
        """
        Calculate Bollinger Bands: middle band (MA), upper, and lower bands.
        """
        if len(klines) < period:
            return {"upper": None, "middle": None, "lower": None, "bandwidth": None}
        
        closes = [float(k.close) for k in klines[-period:]]
        middle = statistics.mean(closes)
        
        # Calculate standard deviation
        variance = sum((x - middle) ** 2 for x in closes) / len(closes)
        std_dev = variance ** 0.5
        
        upper = middle + (std_dev * std_dev_multiplier)
        lower = middle - (std_dev * std_dev_multiplier)
        bandwidth = ((upper - lower) / middle * 100) if middle else 0
        
        # Calculate position within bands (0-1, where 0 = at lower, 1 = at upper)
        current_price = closes[-1]
        if upper == lower:
            position = 0.5
        else:
            position = (current_price - lower) / (upper - lower)
        
        return {
            "upper": round(upper, 2),
            "middle": round(middle, 2),
            "lower": round(lower, 2),
            "bandwidth": round(bandwidth, 2),
            "position": round(max(0, min(1, position)), 2),  # 0-1 range
            "interpretation": "overbought" if position > 0.8 else "oversold" if position < 0.2 else "neutral"
        }

    @staticmethod
    def calculate_stochastic(klines: List[KlineData], period: int = 14, smooth: int = 3) -> dict:
        """
        Calculate Stochastic Oscillator.
        Measures momentum and trend strength.
        """
        if len(klines) < period:
            return {"k": None, "d": None}
        
        recent = klines[-period:]
        highs = [float(k.high) for k in recent]
        lows = [float(k.low) for k in recent]
        closes = [float(k.close) for k in recent]
        
        highest_high = max(highs)
        lowest_low = min(lows)
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            k_percent = 50.0
        else:
            k_percent = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        
        return {
            "k": round(k_percent, 2),
            "interpretation": "overbought" if k_percent > 80 else "oversold" if k_percent < 20 else "neutral"
        }

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
