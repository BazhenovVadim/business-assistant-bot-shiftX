from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import BusinessData


class BusinessDataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, business_data: BusinessData) -> BusinessData:
        """Сохранить бизнес-данные"""
        self.session.add(business_data)
        await self.session.commit()
        await self.session.refresh(business_data)
        return business_data

    async def find_by_user_and_type(self, user_id: int, data_type: str, limit: int = 5) -> Sequence[BusinessData]:
        """Найти данные пользователя по типу"""
        result = await self.session.execute(
            select(BusinessData)
            .where(
                and_(
                    BusinessData.user_id == user_id,
                    BusinessData.data_type == data_type
                )
            )
            .order_by(BusinessData.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def find_latest_by_type(self, user_id: int, data_type: str) -> Optional[BusinessData]:
        """Найти последние данные по типу"""
        result = await self.session.execute(
            select(BusinessData)
            .where(
                and_(
                    BusinessData.user_id == user_id,
                    BusinessData.data_type == data_type
                )
            )
            .order_by(BusinessData.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
