from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import QuickAction


class QuickActionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, quick_action: QuickAction) -> QuickAction:
        """Сохранить действие"""
        self.session.add(quick_action)
        await self.session.commit()
        await self.session.refresh(quick_action)
        return quick_action

    async def find_recent_actions(self, user_id: int, limit: int = 10) -> Sequence[QuickAction]:
        """Найти последние действия пользователя"""
        result = await self.session.execute(
            select(QuickAction)
            .where(QuickAction.user_id == user_id)
            .order_by(QuickAction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
