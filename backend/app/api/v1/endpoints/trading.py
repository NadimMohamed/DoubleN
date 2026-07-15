from fastapi import APIRouter, Path, Query, HTTPException
from datetime import datetime, timezone
from typing import Optional
import structlog

from app.services.binance import binance_client
from app.services.trading_analysis import (
    TrendAnalysis, TechnicalIndicators, SupportResistance,
    SignalGenerator, RiskManagement
)
from app.schemas.market import SUPPORTED_SYMBOLS
from app.schemas.trading import TradeAnalysisResponse, TrendResponse, SupportResistanceResponse, IndicatorResponse, SignalResponse, RiskManagementResponse
from app.core.exceptions import InvalidSymbolError, ValidationError

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/trading", tags=["trading"])

def _validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol must not be empty")
    s = symbol.strip().upper()
    if s not in SUPPORTED_SYMBOLS:
        raise InvalidSymbolError(s, SUPPORTED_SYMBOLS)
    return s

@router.get("/analysis/{symbol}", response_model=TradeAnalysisResponse)
async def get_trade_analysis(
    symbol: str = Path(...),
    interval: str = Query(default="1h"),
    lookback: int = Query(default=100, ge=50, le=500),
    entry_price: Optional[float] = Query(default=None),
    account_balance: float = Query(default=10000.0, gt=0),
):
    """AI trading analysis with signals and risk management."""
    symbol = _validate_symbol(symbol)
    
    try:
        klines = await binance_client.get_klines(symbol, interval, lookback)
        if not klines:
            raise HTTPException(status_code=502, detail="Unable to fetch market data")
        
        ticker = await binance_client.get_ticker_24h(symbol)
        current_price = ticker.price
        
        trend, trend_strength = TrendAnalysis.detect_trend(klines)
        rsi = TechnicalIndicators.calculate_rsi(klines)
        sr = SupportResistance.calculate_levels(klines)
        signal, confidence, reasoning = SignalGenerator.generate_signal(trend, rsi, current_price, sr)
        
        entry = entry_price or current_price
        stop_loss = RiskManagement.calculate_stop_loss(entry)
        tp_2x = RiskManagement.calculate_take_profit(entry, 2)
        tp_3x = RiskManagement.calculate_take_profit(entry, 3)
        pos_size = RiskManagement.calculate_position_size(account_balance, entry, stop_loss)
        
        log.info("trading.analysis", symbol=symbol, signal=signal.value)
        
        return TradeAnalysisResponse(
            symbol=symbol,
            current_price=current_price,
            trend=TrendResponse(direction=trend.value, strength=trend_strength),
            support_resistance=SupportResistanceResponse(**sr),
            indicators=IndicatorResponse(rsi=rsi),
            signal=SignalResponse(signal=signal.value, confidence=confidence, reasoning=reasoning),
            risk_management=RiskManagementResponse(
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit_2x=tp_2x,
                take_profit_3x=tp_3x,
                position_size=pos_size["position_size"],
                risk_amount=pos_size["risk_amount"],
            ),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error("trading.error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend/{symbol}", response_model=TrendResponse)
async def get_trend(symbol: str = Path(...), interval: str = Query(default="1h")):
    """Quick trend detection."""
    symbol = _validate_symbol(symbol)
    try:
        klines = await binance_client.get_klines(symbol, interval, 20)
        if not klines:
            raise HTTPException(status_code=502, detail="Unable to fetch market data")
        trend, strength = TrendAnalysis.detect_trend(klines)
        return TrendResponse(direction=trend.value, strength=strength)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support-resistance/{symbol}", response_model=SupportResistanceResponse)
async def get_sr(symbol: str = Path(...), interval: str = Query(default="1h"), period: int = Query(default=20, ge=5, le=100)):
    """Support and resistance levels."""
    symbol = _validate_symbol(symbol)
    try:
        klines = await binance_client.get_klines(symbol, interval, period)
        if not klines:
            raise HTTPException(status_code=502, detail="Unable to fetch market data")
        sr = SupportResistance.calculate_levels(klines, period)
        return SupportResistanceResponse(**sr)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
