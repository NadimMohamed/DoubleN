from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.watchlist import WatchlistService
from app.services.binance import binance_client
from app.schemas.market import WatchlistAdd, WatchlistItemResponse, WatchlistWithPrice
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/watchlist", tags=["watchlist"])

MAX_WATCHLIST_ITEMS = 20


@router.get(
    "",
    response_model=list[WatchlistWithPrice],
    summary="Get user watchlist with live Binance prices",
)
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await WatchlistService.get_user_watchlist(db, current_user.id)
    if not items:
        return []

    # Fetch live prices for all symbols in one batch request
    symbols = [item.symbol for item in items]
    try:
        tickers = await binance_client.get_multiple_tickers(symbols)
        ticker_map = {t.symbol: t for t in tickers}
    except Exception as e:
        log.warning("watchlist.price_fetch_failed", error=str(e))
        ticker_map = {}

    result = []
    for item in items:
        ticker = ticker_map.get(item.symbol)
        result.append(WatchlistWithPrice(
            id=item.id,
            symbol=item.symbol,
            base_asset=item.base_asset,
            quote_asset=item.quote_asset,
            added_at=item.added_at,
            price=ticker.price if ticker else None,
            price_change_24h=ticker.price_change if ticker else None,
            price_change_pct_24h=ticker.price_change_pct if ticker else None,
            high_24h=ticker.high_24h if ticker else None,
            low_24h=ticker.low_24h if ticker else None,
            volume_24h=ticker.volume if ticker else None,
            quote_volume_24h=ticker.quote_volume if ticker else None,
        ))
    return result


@router.post(
    "",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a symbol to watchlist",
)
async def add_to_watchlist(
    data: WatchlistAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await WatchlistService.count_items(db, current_user.id)
    if count >= MAX_WATCHLIST_ITEMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Watchlist limit reached ({MAX_WATCHLIST_ITEMS} items max)",
        )

    try:
        item = await WatchlistService.add_symbol(db, current_user.id, data.symbol)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a symbol from watchlist",
)
async def remove_from_watchlist(
    item_id: uuid.UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await WatchlistService.remove_symbol(db, current_user.id, item_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
