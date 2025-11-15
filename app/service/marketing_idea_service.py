from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import MarketingIdeas
from app.service import  LLMService


class MarketingIdeaService:

    @staticmethod
    async def generate_marketing_idea(
            db: AsyncSession,
            user_id: int,
            niche: str,
            goal: str,
            platform: str,
            custom_request: Optional[str] = None
    ):
        """
        Генерация маркетинговых идей для малого бизнеса
        """

        prompt = MarketingIdeaService._build_prompt(
            niche=niche,
            goal=goal,
            platform=platform,
            custom_request=custom_request
        )
        llm_service = LLMService()
        llm_response = await llm_service.generate(prompt)

        idea_title = llm_response.get("title")
        idea_description = llm_response.get("description")
        idea_examples = llm_response.get("examples")

        db_item = MarketingIdeas(
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

        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)

        return db_item

    @staticmethod
    def _build_prompt(niche: str, goal: str, platform: str, custom_request: Optional[str]):
        """
        Промпт, который уходит в LLM
        """

        return f"""
Ты — эксперт по маркетингу малого бизнеса. 
Твоя задача — придумать мощную маркетинговую идею.

Данные бизнеса:
- Ниша: {niche}
- Цель: {goal}
- Площадка: {platform}

Дополнительный запрос:
{custom_request or "нет"}

Сформируй результат в JSON:
{{
    "title": "короткое название идеи",
    "description": "глубокое описание, как реализовать",
    "examples": "несколько примеров постов/формулировок"
}}
        """
