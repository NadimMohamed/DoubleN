from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.position import Position, PositionStatus, PositionSide
from app.schemas.position import PositionCreate, PositionResponse
from datetime import datetime, timezone
import uuid

class PositionService:
    @staticmethod
    async def create_position(db: AsyncSession, user_id: str, data: PositionCreate) -> PositionResponse:
        position = Position(
            id=str(uuid.uuid4()),
            user_id=user_id,
            symbol=data.symbol.upper(),
            side=PositionSide(data.side.lower()),
            quantity=data.quantity,
            entry_price=data.entry_price,
            current_price=data.entry_price,
            leverage=data.leverage,
            stop_loss=data.stop_loss,
            take_profit=data.take_profit,
        )
        db.add(position)
        await db.commit()
        await db.refresh(position)
        return PositionResponse.model_validate(position)

    @staticmethod
    async def get_open_positions(db: AsyncSession, user_id: str) -> list[PositionResponse]:
        query = select(Position).where(
            (Position.user_id == user_id) & (Position.status == PositionStatus.OPEN)
        ).order_by(Position.opened_at.desc())
        result = await db.execute(query)
        positions = result.scalars().all()
        return [PositionResponse.model_validate(p) for p in positions]

    @staticmethod
    async def calculate_pnl(position: Position) -> tuple[float, float]:
        if position.side == PositionSide.LONG:
            pnl = (position.current_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - position.current_price) * position.quantity

        pnl_pct = (pnl / (position.entry_price * position.quantity)) * 100 if position.entry_price > 0 else 0
        return pnl, pnl_pct

    @staticmethod
    async def update_position_price(db: AsyncSession, position_id: str, current_price: float) -> PositionResponse:
        query = select(Position).where(Position.id == position_id)
        result = await db.execute(query)
        position = result.scalar_one()

        position.current_price = current_price
        pnl, pnl_pct = await PositionService.calculate_pnl(position)
        position.unrealized_pnl = pnl
        position.unrealized_pnl_pct = pnl_pct

        await db.commit()
        await db.refresh(position)
        return PositionResponse.model_validate(position)

    @staticmethod
    async def close_position(db: AsyncSession, position_id: str, exit_price: float) -> PositionResponse:
        query = select(Position).where(Position.id == position_id)
        result = await db.execute(query)
        position = result.scalar_one()

        position.current_price = exit_price
        pnl, pnl_pct = await PositionService.calculate_pnl(position)
        position.realized_pnl = pnl
        position.unrealized_pnl = pnl
        position.unrealized_pnl_pct = pnl_pct
        position.status = PositionStatus.CLOSED
        position.closed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(position)
        return PositionResponse.model_validate(position)
