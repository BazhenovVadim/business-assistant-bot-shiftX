from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database.models import MarketingIdeas


class MarketingIdeaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            user_id: int,
            niche: str,
            goal: str,
            platform: str,
            idea_title: str,
            idea_description: str,
            idea_examples: str,
            custom_request: Optional[str] = None
    ) -> MarketingIdeas:
        """Создать новую маркетинговую идею"""
        idea = MarketingIdeas(
            user_id=user_id,
            niche=niche,
            goal=goal,
            platform=platform,
            custom_request=custom_request,
            idea_title=idea_title,
            idea_description=idea_description,
            idea_examples=idea_examples,
            created_at=datetime.now()
        )
        self.session.add(idea)
        await self.session.flush()
        await self.session.refresh(idea)
        return idea

    async def get_by_user_id(
            self,
            user_id: int,
            limit: int = 10
    ) -> List[MarketingIdeas]:
        """Получить маркетинговые идеи пользователя"""
        result = await self.session.execute(
            select(MarketingIdeas)
            .where(MarketingIdeas.user_id == user_id)
            .order_by(desc(MarketingIdeas.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id_and_user(
            self,
            idea_id: int,
            user_id: int
    ) -> Optional[MarketingIdeas]:
        """Получить идею по ID с проверкой пользователя"""
        result = await self.session.execute(
            select(MarketingIdeas)
            .where(
                MarketingIdeas.id == idea_id,
                MarketingIdeas.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_statistics(
            self,
            user_id: int
    ) -> dict:
        """Получить статистику по маркетинговым идеям пользователя"""
        # Общее количество идей
        total_count_result = await self.session.execute(
            select(MarketingIdeas)
            .where(MarketingIdeas.user_id == user_id)
        )
        total_ideas = total_count_result.scalars().all()

        # Идеи по платформам
        platforms_result = await self.session.execute(
            select(MarketingIdeas.platform)
            .where(MarketingIdeas.user_id == user_id)
            .distinct()
        )
        platforms = [row[0] for row in platforms_result.all()]

        # Последняя идея
        last_idea_result = await self.session.execute(
            select(MarketingIdeas)
            .where(MarketingIdeas.user_id == user_id)
            .order_by(desc(MarketingIdeas.created_at))
            .limit(1)
        )
        last_idea = last_idea_result.scalar_one_or_none()

        return {
            "total_ideas": len(total_ideas),
            "platforms": platforms,
            "last_idea_date": last_idea.created_at if last_idea else None,
            "last_idea_title": last_idea.idea_title if last_idea else None
        }