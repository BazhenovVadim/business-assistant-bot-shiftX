from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database.models import Sale
from datetime import datetime


class SaleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, sale_data: dict) -> Sale:
        """Создать продажу"""
        sale = Sale(**sale_data)
        self.session.add(sale)
        await self.session.flush()
        await self.session.refresh(sale)
        return sale

    async def get_by_period(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Получить продажи за период"""
        result = await self.session.execute(
            select(Sale).where(
                Sale.user_id == user_id,
                Sale.sale_date.between(start_date, end_date)
            )
        )
        return result.scalars().all()

    async def get_by_product(self, product_id: int, user_id: int) -> List[Sale]:
        """Получить продажи по товару"""
        result = await self.session.execute(
            select(Sale).where(
                Sale.product_id == product_id,
                Sale.user_id == user_id
            )
        )
        return result.scalars().all()

    async def get_all(self, user_id: int) -> List[Sale]:
        """Получить все продажи пользователя"""
        result = await self.session.execute(
            select(Sale).where(Sale.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id(self, sale_id: int, user_id: int) -> Optional[Sale]:
        """Найти продажу по ID"""
        result = await self.session.execute(
            select(Sale).where(
                Sale.id == sale_id,
                Sale.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_total_revenue(self, user_id: int, start_date: datetime, end_date: datetime) -> float:
        """Получить общую выручку за период"""
        result = await self.session.execute(
            select(func.sum(Sale.total_amount)).where(
                Sale.user_id == user_id,
                Sale.sale_date.between(start_date, end_date)
            )
        )
        return result.scalar() or 0.0

    async def get_sales_count(self, user_id: int, start_date: datetime, end_date: datetime) -> int:
        """Получить количество продаж за период"""
        result = await self.session.execute(
            select(func.count(Sale.id)).where(
                Sale.user_id == user_id,
                Sale.sale_date.between(start_date, end_date)
            )
        )
        return result.scalar() or 0