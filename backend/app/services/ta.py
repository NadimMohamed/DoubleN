import numpy as np
from typing import Optional
from app.schemas.market import KlineData


class TACalculator:
    @staticmethod
    def sma(prices: list[float], period: int) -> list[Optional[float]]:
        """Simple Moving Average"""
        return [
            sum(prices[max(0, i-period+1):i+1]) / min(i+1, period) if i >= 0 else None
            for i in range(len(prices))
        ]

    @staticmethod
    def rsi(prices: list[float], period: int = 14) -> list[Optional[float]]:
        """Relative Strength Index"""
        if len(prices) < period:
            return [None] * len(prices)

        rsis = [None] * (period - 1)
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        seed = deltas[:period]
        up = sum([d for d in seed if d > 0]) / period
        down = sum([-d for d in seed if d < 0]) / period
        rs = up / down if down != 0 else 0
        rsis.append(100 - 100 / (1 + rs))

        for i in range(period, len(prices)):
            delta = deltas[i - 1]
            up = (up * (period - 1) + (delta if delta > 0 else 0)) / period
            down = (down * (period - 1) + (-delta if delta < 0 else 0)) / period
            rs = up / down if down != 0 else 0
            rsis.append(100 - 100 / (1 + rs))

        return rsis

    @staticmethod
    def macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """MACD indicator"""
        if len(prices) < slow:
            return [], [], []

        ema_fast = TACalculator._ema(prices, fast)
        ema_slow = TACalculator._ema(prices, slow)
        macd_line = [f - s if f and s else None for f, s in zip(ema_fast, ema_slow)]
        signal_line = TACalculator._ema([m for m in macd_line if m], signal)
        histogram = [m - s if m and s else None for m, s in zip(macd_line, signal_line)]

        return macd_line, signal_line, histogram

    @staticmethod
    def _ema(prices: list[float], period: int) -> list[Optional[float]]:
        """Exponential Moving Average"""
        if len(prices) < period:
            return [None] * len(prices)

        emas = [None] * (period - 1)
        ema = sum(prices[:period]) / period
        emas.append(ema)
        k = 2 / (period + 1)

        for price in prices[period:]:
            ema = price * k + ema * (1 - k)
            emas.append(ema)

        return emas

    @staticmethod
    def atr(high: list[float], low: list[float], close: list[float], period: int = 14) -> list[Optional[float]]:
        """Average True Range"""
        if len(high) < period:
            return [None] * len(high)

        tr_values = []
        for i in range(len(high)):
            if i == 0:
                tr = high[i] - low[i]
            else:
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
            tr_values.append(tr)

        atr_values = [None] * (period - 1)
        atr = sum(tr_values[:period]) / period
        atr_values.append(atr)

        for i in range(period, len(tr_values)):
            atr = (atr * (period - 1) + tr_values[i]) / period
            atr_values.append(atr)

        return atr_values

    @staticmethod
    def support_resistance(prices: list[float], window: int = 20) -> tuple[Optional[float], Optional[float]]:
        """Find support and resistance levels"""
        if len(prices) < window:
            return None, None

        recent = prices[-window:]
        support = min(recent)
        resistance = max(recent)

        return support, resistance


ta_calculator = TACalculator()
