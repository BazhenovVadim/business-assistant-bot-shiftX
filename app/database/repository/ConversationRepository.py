from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, conversation: Conversation):
        self.session.add(conversation)
        return conversation

    async def update(self, conversation: Conversation):
        self.session.add(conversation)
        return conversation

    async def find_last_active(self, user_id: int, since):
        result = await self.session.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.last_message_at >= since
            )
            .order_by(Conversation.id.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def find_by_user_id(self, user_id: int, limit: int = 10):
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def find_by_id(self, conversation_id: int):
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalars().first()
