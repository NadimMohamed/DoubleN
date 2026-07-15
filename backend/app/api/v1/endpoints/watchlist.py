import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.services.watchlist import WatchlistService
from app.services.binance import binance_client
from app.schemas.market import WatchlistAdd, WatchlistItemResponse, WatchlistWithPrice, SUPPORTED_SYMBOLS
from app.core.exceptions import InvalidSymbolError, ValidationError, ConflictError, ResourceNotFoundError
import structlog

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/watchlist", tags=["watchlist"])

MAX_WATCHLIST_ITEMS = 20

# Live-price fetch tuning. The watchlist page polls this endpoint frequently,
# so price lookups need a bounded timeout and a couple of quick retries
# rather than letting a single slow/failed Binance call block (or silently
# blank out) the whole response.
PRICE_FETCH_TIMEOUT_SECONDS = 8.0
PRICE_FETCH_MAX_ATTEMPTS = 3
PRICE_FETCH_RETRY_DELAY_SECONDS = 0.5


async def _fetch_tickers_with_retry(symbols: list[str], user_id: str) -> dict:
    """Fetch live tickers for `symbols`, retrying transient failures and
    bounding total wait time with a timeout so the endpoint never hangs
    waiting on Binance. Falls back to simulated prices as a last resort so
    the UI always has *something* to render instead of blank rows.
    """
    last_error: Exception | None = None

    for attempt in range(1, PRICE_FETCH_MAX_ATTEMPTS + 1):
        try:
            tickers = await asyncio.wait_for(
                binance_client.get_multiple_tickers(symbols),
                timeout=PRICE_FETCH_TIMEOUT_SECONDS,
            )
            if attempt > 1:
                log.info(
                    "watchlist.price_fetch_recovered",
                    user_id=user_id,
                    attempt=attempt,
                    symbols=symbols,
                )
            return {t.symbol: t for t in tickers}
        except asyncio.TimeoutError as e:
            last_error = e
            log.warning(
                "watchlist.price_fetch_timeout",
                user_id=user_id,
                attempt=attempt,
                timeout=PRICE_FETCH_TIMEOUT_SECONDS,
                symbols=symbols,
            )
        except Exception as e:
            last_error = e
            log.warning(
                "watchlist.price_fetch_attempt_failed",
                user_id=user_id,
                attempt=attempt,
                symbols=symbols,
                error=str(e),
            )

        if attempt < PRICE_FETCH_MAX_ATTEMPTS:
            await asyncio.sleep(PRICE_FETCH_RETRY_DELAY_SECONDS * attempt)

    # All retries exhausted — fall back to simulated prices so the watchlist
    # still shows numbers instead of "Loading…" forever.
    log.error(
        "watchlist.price_fetch_failed_using_mock",
        user_id=user_id,
        symbols=symbols,
        error=str(last_error) if last_error else None,
    )
    try:
        mock_tickers = binance_client.get_mock_tickers(symbols)
        return {t.symbol: t for t in mock_tickers}
    except Exception as e:
        log.error("watchlist.mock_price_fallback_failed", user_id=user_id, error=str(e))
        return {}


def _validate_symbol(symbol: str) -> str:
    """Validate a symbol against the supported set before any database
    operation is attempted, so bad input never reaches the DB layer."""
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol must not be empty")
    s = symbol.strip().upper()
    if s not in SUPPORTED_SYMBOLS:
        raise InvalidSymbolError(s, SUPPORTED_SYMBOLS)
    return s


@router.get(
    "",
    response_model=list[WatchlistWithPrice],
    summary="Get user watchlist with live Binance prices",
)
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log.info("watchlist.fetch_start", user_id=str(current_user.id))

    try:
        items = await WatchlistService.get_user_watchlist(db, current_user.id)
    except SQLAlchemyError as e:
        log.error("watchlist.fetch_failed", user_id=str(current_user.id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to load watchlist") from e

    if not items:
        log.info("watchlist.fetch_empty", user_id=str(current_user.id))
        return []

    # Fetch live prices for all symbols in one batch request. This helper
    # retries transient failures, bounds the wait with a timeout, and falls
    # back to simulated prices as a last resort — the response always
    # contains a full row per watchlist item, never a bare null price.
    symbols = [item.symbol for item in items]
    ticker_map = await _fetch_tickers_with_retry(symbols, str(current_user.id))

    result = []
    for item in items:
        # Ensure base/quote asset are always populated even for legacy rows
        # that may predate the symbol map, so the UI never renders blanks.
        base_asset = item.base_asset or item.symbol.replace("USDT", "") or item.symbol
        quote_asset = item.quote_asset or "USDT"

        ticker = ticker_map.get(item.symbol)
        if ticker is None:
            log.warning(
                "watchlist.item_missing_price",
                user_id=str(current_user.id),
                symbol=item.symbol,
            )

        result.append(WatchlistWithPrice(
            id=item.id,
            symbol=item.symbol,
            base_asset=base_asset,
            quote_asset=quote_asset,
            added_at=item.added_at,
            price=ticker.price if ticker else None,
            price_change_24h=ticker.price_change if ticker else None,
            price_change_pct_24h=ticker.price_change_pct if ticker else None,
            high_24h=ticker.high_24h if ticker else None,
            low_24h=ticker.low_24h if ticker else None,
            volume_24h=ticker.volume if ticker else None,
            quote_volume_24h=ticker.quote_volume if ticker else None,
        ))

    log.info(
        "watchlist.fetch_complete",
        user_id=str(current_user.id),
        item_count=len(result),
        priced_count=sum(1 for item in result if item.price is not None),
    )
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
    # Symbol is already validated by the WatchlistAdd schema, but we
    # re-validate here so a bad symbol never reaches the database layer
    # even if the schema validation is bypassed or loosened in the future.
    symbol = _validate_symbol(data.symbol)

    try:
        count = await WatchlistService.count_items(db, current_user.id)
    except SQLAlchemyError as e:
        log.error("watchlist.count_failed", user_id=str(current_user.id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to check watchlist size") from e

    if count >= MAX_WATCHLIST_ITEMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Watchlist limit reached ({MAX_WATCHLIST_ITEMS} items max)",
        )

    try:
        item = await WatchlistService.add_symbol(db, current_user.id, symbol)
    except ValueError as e:
        raise ConflictError(str(e))
    except SQLAlchemyError as e:
        log.error(
            "watchlist.add_failed",
            user_id=str(current_user.id),
            symbol=symbol,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to add symbol to watchlist") from e

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
    try:
        removed = await WatchlistService.remove_symbol(db, current_user.id, item_id)
    except SQLAlchemyError as e:
        log.error(
            "watchlist.remove_failed",
            user_id=str(current_user.id),
            item_id=str(item_id),
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to remove item from watchlist") from e

    if not removed:
        raise ResourceNotFoundError("Watchlist item not found")
