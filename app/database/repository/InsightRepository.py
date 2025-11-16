from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Insight


class InsightRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            document_id: int,
            summary: str,
            risks: str,
            recommendations: str,
            raw_data: str
    ) -> Insight:
        insight = Insight(
            document_id=document_id,
            summary=summary,
            risks=risks,
            recommendations=recommendations,
            raw_data=raw_data
        )
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def get_by_document_id(self, document_id: int) -> Insight:
        result = await self.session.execute(
            select(Insight).where(Insight.document_id == document_id)
        )
        return result.scalar_one_or_none()