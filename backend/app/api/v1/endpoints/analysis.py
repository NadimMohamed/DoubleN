from fastapi import APIRouter, Path, Query, HTTPException
from app.services.binance import binance_client
from app.services.ai import ai_analyzer
from app.schemas.trading import MarketAnalysis
from app.schemas.market import SUPPORTED_SYMBOLS
from app.core.exceptions import InvalidSymbolError
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/{symbol}", response_model=MarketAnalysis)
async def get_market_analysis(
    symbol: str = Path(..., description="e.g. BTCUSDT"),
    interval: str = Query(default="1h", description="Candle interval"),
):
    """Get comprehensive market analysis with AI signal and technical indicators."""
    symbol = symbol.upper()
    if symbol not in SUPPORTED_SYMBOLS:
        raise InvalidSymbolError(symbol, list(SUPPORTED_SYMBOLS))
    
    try:
        ticker = await binance_client.get_ticker_24h(symbol)
        klines = await binance_client.get_klines(symbol, interval, limit=200)
        analysis = await ai_analyzer.analyze_market(ticker, klines)
        log.info("analysis.generated", symbol=symbol, signal=analysis.signal.signal.value, confidence=analysis.signal.confidence)
        return analysis
    except Exception as e:
        log.error("analysis.failed", symbol=symbol, error=str(e))
        raise HTTPException(status_code=503, detail="Analysis temporarily unavailable")
