from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
import uuid
import structlog

from app.models.watchlist import WatchlistItem
from app.schemas.market import SUPPORTED_SYMBOLS

log = structlog.get_logger(__name__)

# Maps symbol → (base, quote)
SYMBOL_MAP = {
    "BTCUSDT":   ("BTC", "USDT"),
    "ETHUSDT":   ("ETH", "USDT"),
    "LTCUSDT":   ("LTC", "USDT"),
    "SOLUSDT":   ("SOL", "USDT"),
    "BNBUSDT":   ("BNB", "USDT"),
    "XRPUSDT":   ("XRP", "USDT"),
    "ADAUSDT":   ("ADA", "USDT"),
    "DOGEUSDT":  ("DOGE", "USDT"),
    "MATICUSDT": ("MATIC", "USDT"),
    "DOTUSDT":   ("DOT", "USDT"),
    "AVAXUSDT":  ("AVAX", "USDT"),
    "LINKUSDT":  ("LINK", "USDT"),
}


class WatchlistService:

    @staticmethod
    async def get_user_watchlist(db: AsyncSession, user_id: uuid.UUID) -> list[WatchlistItem]:
        result = await db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user_id)
            .order_by(WatchlistItem.added_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def add_symbol(
        db: AsyncSession, user_id: uuid.UUID, symbol: str
    ) -> WatchlistItem:
        symbol = symbol.upper()

        # Check already in watchlist
        existing = await db.execute(
            select(WatchlistItem).where(
                WatchlistItem.user_id == user_id,
                WatchlistItem.symbol == symbol,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"{symbol} is already in your watchlist")

        base, quote = SYMBOL_MAP.get(symbol, (symbol[:-4], "USDT"))

        item = WatchlistItem(
            user_id=user_id,
            symbol=symbol,
            base_asset=base,
            quote_asset=quote,
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        log.info("watchlist.added", user_id=str(user_id), symbol=symbol)
        return item

    @staticmethod
    async def remove_symbol(
        db: AsyncSession, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> bool:
        result = await db.execute(
            delete(WatchlistItem).where(
                WatchlistItem.id == item_id,
                WatchlistItem.user_id == user_id,
            )
        )
        deleted = result.rowcount > 0
        if deleted:
            log.info("watchlist.removed", user_id=str(user_id), item_id=str(item_id))
        return deleted

    @staticmethod
    async def count_items(db: AsyncSession, user_id: uuid.UUID) -> int:
        result = await db.execute(
            select(WatchlistItem).where(WatchlistItem.user_id == user_id)
        )
        return len(result.scalars().all())
