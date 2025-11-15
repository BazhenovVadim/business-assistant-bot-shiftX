from typing import List, Optional, Dict, Any
from app.database.unit_of_work import UnitOfWork
from app.database.models import Conversation


class ConversationService:
    def __init__(self, db):
        self.db = db

    async def save_conversation(self, user_id: int, user_message: str, bot_response: str,
                                category: str = None) -> Conversation:
        """Сохранить диалог"""
        async with self.db.get_uow() as uow:
            conversation = Conversation(
                user_id=user_id,
                user_message=user_message,
                bot_response=bot_response,
                category=category,
                message_length=len(user_message)
            )
            return await uow.conversations.save(conversation)

    async def get_user_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Получить историю диалогов пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.conversations.find_by_user_id(user_id, limit)

    async def get_conversations_by_category(self, user_id: int, category: str) -> List[Conversation]:
        """Получить диалоги по категории"""
        async with self.db.get_uow() as uow:
            return await uow.conversations.find_by_category(user_id, category)

    async def get_analytics(self, user_id: int) -> Dict[str, Any]:
        """Аналитика по диалогам пользователя"""
        async with self.db.get_uow() as uow:
            total_conversations = await uow.conversations.count_by_user(user_id)

            # Распределение по категориям
            conversations = await uow.conversations.find_by_user_id(user_id, limit=100)
            category_stats = {}
            for conv in conversations:
                category = conv.category or "general"
                category_stats[category] = category_stats.get(category, 0) + 1

            return {
                "total_conversations": total_conversations,
                "category_distribution": category_stats,
                "most_active_category": max(category_stats.items(), key=lambda x: x[1]) if category_stats else None
            }