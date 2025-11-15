from typing import List, Sequence, Any

from sqlalchemy import select, update, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Template


class TemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(self) -> Sequence[Template]:
        """Найти все шаблоны"""
        result = await self.session.execute(
            select(Template).order_by(Template.usage_count.desc())
        )
        return result.scalars().all()

    async def find_by_category(self, category: str) -> Sequence[Template]:
        """Найти шаблоны по категории"""
        result = await self.session.execute(
            select(Template)
            .where(Template.category == category)
            .order_by(Template.usage_count.desc())
        )
        return result.scalars().all()

    async def increment_usage(self, template_id: int) -> None:
        """Увеличить счетчик использования"""
        await self.session.execute(
            update(Template)
            .where(Template.id == template_id)
            .values(usage_count=Template.usage_count + 1)
        )
        await self.session.commit()