from app.services.ta import ta_calculator
from app.schemas.trading import Signal, SignalType, Trend, TrendDirection, Indicators, SupportResistance, MarketAnalysis
from app.schemas.market import TickerPrice, KlineData
from typing import Optional
import structlog

log = structlog.get_logger(__name__)

class AIAnalyzer:
    @staticmethod
    async def analyze_market(ticker: TickerPrice, klines: list[KlineData]) -> MarketAnalysis:
        closes = [float(k.close) for k in klines]
        highs = [float(k.high) for k in klines]
        lows = [float(k.low) for k in klines]
        
        rsi_values = ta_calculator.rsi(closes)
        rsi = rsi_values[-1] if rsi_values else None
        
        macd_line, macd_signal, _ = ta_calculator.macd(closes)
        macd = macd_line[-1] if macd_line else None
        macd_sig = macd_signal[-1] if macd_signal else None
        
        ema_12 = ta_calculator._ema(closes, 12)[-1] if len(closes) >= 12 else None
        ema_26 = ta_calculator._ema(closes, 26)[-1] if len(closes) >= 26 else None
        
        atr_values = ta_calculator.atr(highs, lows, closes)
        atr = atr_values[-1] if atr_values else None
        
        support, resistance = ta_calculator.support_resistance(closes)
        
        trend = AIAnalyzer._calculate_trend(closes, rsi, ema_12, ema_26, macd, macd_sig)
        signal = AIAnalyzer._generate_signal(ticker.price, closes, rsi, macd, macd_sig, ema_12, ema_26, support, resistance, trend)
        
        return MarketAnalysis(
            symbol=ticker.symbol,
            current_price=ticker.price,
            signal=signal,
            trend=trend,
            support_resistance=SupportResistance(support=support, resistance=resistance),
            indicators=Indicators(rsi=rsi, macd=macd, macd_signal=macd_sig, ema_12=ema_12, ema_26=ema_26, atr=atr)
        )
    
    @staticmethod
    def _calculate_trend(closes: list, rsi: Optional[float], ema_12: Optional[float], ema_26: Optional[float], macd: Optional[float], macd_sig: Optional[float]) -> Trend:
        bullish_signals = 0
        total_signals = 0
        
        if ema_12 and ema_26:
            total_signals += 1
            if ema_12 > ema_26:
                bullish_signals += 1
        
        if rsi:
            total_signals += 1
            if 50 < rsi < 70:
                bullish_signals += 0.5
            elif rsi >= 70:
                bullish_signals += 1
            elif rsi < 30:
                bullish_signals -= 0.5
        
        if macd and macd_sig:
            total_signals += 1
            if macd > macd_sig:
                bullish_signals += 1
        
        if len(closes) >= 2:
            total_signals += 1
            if closes[-1] > closes[-2]:
                bullish_signals += 0.5
        
        if total_signals == 0:
            return Trend(direction=TrendDirection.NEUTRAL, strength=0)
        
        strength = (bullish_signals / total_signals) * 100
        direction = TrendDirection.BULLISH if strength >= 65 else TrendDirection.BEARISH if strength <= 35 else TrendDirection.NEUTRAL
        return Trend(direction=direction, strength=round(strength))
    
    @staticmethod
    def _generate_signal(current_price: float, closes: list, rsi: Optional[float], macd: Optional[float], macd_sig: Optional[float], ema_12: Optional[float], ema_26: Optional[float], support: Optional[float], resistance: Optional[float], trend: Trend) -> Signal:
        buy_points = 0
        sell_points = 0
        reasoning_parts = []
        
        if rsi:
            if rsi < 30:
                buy_points += 2
                reasoning_parts.append("RSI oversold")
            elif rsi < 40:
                buy_points += 1
            elif rsi > 70:
                sell_points += 2
                reasoning_parts.append("RSI overbought")
            elif rsi > 60:
                sell_points += 1
        
        if macd and macd_sig:
            if macd > macd_sig:
                buy_points += 1
                reasoning_parts.append("MACD bullish")
            elif macd < macd_sig:
                sell_points += 1
                reasoning_parts.append("MACD bearish")
        
        if ema_12 and ema_26:
            if ema_12 > ema_26:
                buy_points += 1
            else:
                sell_points += 1
        
        if trend.direction == TrendDirection.BULLISH:
            buy_points += 1
        elif trend.direction == TrendDirection.BEARISH:
            sell_points += 1
        
        total_points = buy_points + sell_points
        
        if buy_points > sell_points:
            signal_type = SignalType.BUY
            confidence = (buy_points / max(total_points, 1)) * 100
        elif sell_points > buy_points:
            signal_type = SignalType.SELL
            confidence = (sell_points / max(total_points, 1)) * 100
        else:
            signal_type = SignalType.NEUTRAL
            confidence = 50.0
        
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Mixed signals"
        return Signal(signal=signal_type, confidence=round(min(confidence, 95)), reasoning=reasoning)

ai_analyzer = AIAnalyzer()
