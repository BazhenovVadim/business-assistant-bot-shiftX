from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select

from app.database.unit_of_work import UnitOfWork
from app.database.models import Conversation


class ConversationService:
    def __init__(self, db):
        self.db = db

    async def add_message(self, user_id: int, user_text: str, bot_text: str, category: str = "general") -> Conversation:
        """Добавляем сообщение в активный диалог (12 часов) через UoW."""
        now = datetime.utcnow()
        user_line = f"USER: {user_text}"
        bot_line = f"BOT: {bot_text}"

        async with self.db.get_uow() as uow:
            # --- ищем последний активный диалог ---
            twelve_hours_ago = now - timedelta(hours=12)
            result = await uow.conversations.session.execute(
                select(Conversation)
                .where(
                    Conversation.user_id == user_id,
                    Conversation.last_message_at >= twelve_hours_ago
                )
                .order_by(Conversation.id.desc())
                .limit(1)
            )
            conv = result.scalar_one_or_none()

            if conv:
                # продолжаем существующий диалог
                conv.user_message += f"\n\n{user_line}"
                conv.bot_response += f"\n\n{bot_line}"
                conv.last_message_at = now
            else:
                # создаём новый диалог
                conv = Conversation(
                    user_id=user_id,
                    category=category,
                    user_message=user_line,
                    bot_response=bot_line,
                    message_length=len(user_text),
                    response_time_ms=0,
                    created_at=now,
                    last_message_at=now,
                )
                await uow.conversations.save(conv)

        return conv
    async def get_user_conversations(self, user_id: int, limit: int = 10):
        async with self.db.get_uow() as uow:
            return await uow.conversations.find_by_user_id(user_id, limit)

    async def get_conversation(self, conversation_id: int):
        async with self.db.get_uow() as uow:
            return await uow.conversations.find_by_id(conversation_id)

