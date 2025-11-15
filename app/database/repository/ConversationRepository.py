from typing import List, Sequence

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, conversation: Conversation) -> Conversation:
        """Сохранить диалог"""
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def find_by_user_id(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Найти диалоги пользователя"""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def find_by_category(self, user_id: int, category: str) -> Sequence[Conversation]:
        """Найти диалоги по категории"""
        result = await self.session.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.category == category
                )
            )
            .order_by(Conversation.created_at.desc())
        )
        return result.scalars().all()

    async def count_by_user(self, user_id: int) -> int:
        """Количество диалогов пользователя"""
        result = await self.session.execute(
            select(func.count(Conversation.id))
            .where(Conversation.user_id == user_id)
        )
        return result.scalar()
