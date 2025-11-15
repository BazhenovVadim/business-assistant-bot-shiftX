from typing import Optional, Dict, Any, List
from app.database.unit_of_work import UnitOfWork
from app.database.models import User


class UserService:
    def __init__(self, db):
        self.db = db

    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None,
                                 last_name: str = None) -> User:
        """Получить или создать пользователя"""
        async with self.db.get_uow() as uow:
            user = await uow.users.find_by_id(user_id)

            if not user:
                user = User(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                user = await uow.users.save(user)
            else:
                await uow.users.update_last_active(user_id)

            return user

    async def update_user_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить профиль пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.users.update_profile(user_id, **kwargs)

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        async with self.db.get_uow() as uow:
            consultations_count = await uow.conversations.count_by_user(user_id)

            conversations = await uow.conversations.find_by_user_id(user_id, limit=50)
            category_counts = {}
            for conv in conversations:
                if conv.category:
                    category_counts[conv.category] = category_counts.get(conv.category, 0) + 1

            popular_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "consultations_count": consultations_count,
                "popular_categories": popular_categories
            }