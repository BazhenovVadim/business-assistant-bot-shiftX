from datetime import datetime
from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import StockMovement


class StockMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, movement_data: dict) -> StockMovement:
        """Создать движение товара"""
        movement = StockMovement(**movement_data)
        self.session.add(movement)
        await self.session.flush()
        await self.session.refresh(movement)
        return movement

    async def get_by_product(self, product_id: int, user_id: int) -> List[StockMovement]:
        """Получить движения по товару"""
        result = await self.session.execute(
            select(StockMovement).where(
                StockMovement.product_id == product_id,
                StockMovement.user_id == user_id
            )
        )
        return result.scalars().all()

    async def get_by_period(self, user_id: int, start_date: datetime, end_date: datetime) -> List[StockMovement]:
        """Получить движения за период"""
        result = await self.session.execute(
            select(StockMovement).where(
                StockMovement.user_id == user_id,
                StockMovement.date.between(start_date, end_date)
            )
        )
        return result.scalars().all()

    async def get_all(self, user_id: int) -> List[StockMovement]:
        """Получить все движения пользователя"""
        result = await self.session.execute(
            select(StockMovement).where(StockMovement.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id(self, movement_id: int, user_id: int) -> Optional[StockMovement]:
        """Найти движение по ID"""
        result = await self.session.execute(
            select(StockMovement).where(
                StockMovement.id == movement_id,
                StockMovement.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_type(self, movement_type: str, user_id: int) -> List[StockMovement]:
        """Получить движения по типу"""
        result = await self.session.execute(
            select(StockMovement).where(
                StockMovement.user_id == user_id,
                StockMovement.type == movement_type
            )
        )
        return result.scalars().all()

    async def get_incoming_movements(self, user_id: int, start_date: datetime, end_date: datetime) -> Sequence[
        StockMovement]:
        """Получить поступления за период"""
        result = await self.session.execute(
            select(StockMovement).where(
                StockMovement.user_id == user_id,
                StockMovement.type == "incoming",
                StockMovement.date.between(start_date, end_date)
            )
        )
        return result.scalars().all()