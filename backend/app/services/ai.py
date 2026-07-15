"""
AI-assisted market analysis service.

Combines trend detection, technical indicators (RSI, MACD, EMA, ATR) and a
rule-based trading signal into a single `MarketAnalysis` response. The
signal generation itself is deterministic technical analysis (see
`app.services.trading_analysis`) rather than a call to an external LLM —
"AI" here refers to the produced signal + reasoning, not the underlying
implementation.
"""
from typing import List
import structlog

from app.schemas.market import TickerPrice, KlineData
from app.schemas.trading import (
    MarketAnalysis,
    Signal,
    SignalType,
    Trend,
    TrendDirection,
    SupportResistance,
    Indicators,
)
from app.services.trading_analysis import (
    TrendAnalysis,
    TechnicalIndicators,
    SupportResistance as SupportResistanceCalculator,
    SignalGenerator,
    SignalType as TASignalType,
)
from app.services.ta import TACalculator

log = structlog.get_logger(__name__)


class AIAnalyzer:
    """Generates a comprehensive market analysis for a symbol."""

    async def analyze_market(self, ticker: TickerPrice, klines: List[KlineData]) -> MarketAnalysis:
        current_price = ticker.price

        trend_direction, trend_strength = TrendAnalysis.detect_trend(klines)
        rsi = TechnicalIndicators.calculate_rsi(klines)
        macd = TechnicalIndicators.calculate_macd(klines)
        sr = SupportResistanceCalculator.calculate_levels(klines)

        signal_type, confidence, reasoning = SignalGenerator.generate_signal(
            trend_direction, rsi, current_price, sr
        )

        closes = [float(k.close) for k in klines]
        highs = [float(k.high) for k in klines]
        lows = [float(k.low) for k in klines]

        ema_12_series = TACalculator._ema(closes, 12)
        ema_26_series = TACalculator._ema(closes, 26)
        atr_series = TACalculator.atr(highs, lows, closes)

        ema_12 = ema_12_series[-1] if ema_12_series else None
        ema_26 = ema_26_series[-1] if ema_26_series else None
        atr = atr_series[-1] if atr_series else None

        signal = Signal(
            signal=self._map_signal(signal_type),
            confidence=confidence,
            reasoning=reasoning or "No strong signal detected",
        )
        trend = Trend(direction=TrendDirection(trend_direction.value), strength=trend_strength)
        support_resistance = SupportResistance(support=sr.get("support"), resistance=sr.get("resistance"))
        indicators = Indicators(
            rsi=rsi,
            macd=macd.get("macd"),
            macd_signal=macd.get("signal"),
            ema_12=round(ema_12, 4) if ema_12 is not None else None,
            ema_26=round(ema_26, 4) if ema_26 is not None else None,
            atr=round(atr, 4) if atr is not None else None,
        )

        return MarketAnalysis(
            symbol=ticker.symbol,
            current_price=current_price,
            signal=signal,
            trend=trend,
            support_resistance=support_resistance,
            indicators=indicators,
        )

    @staticmethod
    def _map_signal(signal_type: TASignalType) -> SignalType:
        mapping = {
            TASignalType.BUY: SignalType.BUY,
            TASignalType.SELL: SignalType.SELL,
            TASignalType.HOLD: SignalType.NEUTRAL,
        }
        return mapping.get(signal_type, SignalType.NEUTRAL)


ai_analyzer = AIAnalyzer()
