from datetime import timedelta, datetime
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
            user = await uow.users.find_by_id(user_id)
            if not user:
                return None

            # Обновляем поля
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)

            user.last_active = datetime.now()
            return user

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        async with self.db.get_uow() as uow:
            # Основная информация о пользователе
            user = await uow.users.find_by_id(user_id)
            if not user:
                return {"error": "Пользователь не найден"}

            # Статистика консультаций
            conversations = await uow.conversations.find_by_user_id(user_id)

            # Популярные категории
            category_stats = {}
            for conv in conversations:
                category = conv.category or "general"
                category_stats[category] = category_stats.get(category, 0) + 1

            popular_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:3]

            # Активность за последние 7 дней
            week_ago = datetime.now() - timedelta(days=7)
            recent_conversations = [c for c in conversations if c.created_at >= week_ago]

            return {
                "user_id": user_id,
                "consultations_count": len(conversations),
                "recent_consultations": len(recent_conversations),
                "popular_categories": popular_categories,
                "first_consultation": conversations[0].created_at if conversations else None,
                "last_consultation": conversations[-1].created_at if conversations else None,
                "account_created": user.created_at,
                "last_active": user.last_active,
                "business_type": user.business_type,
                "industry": user.industry
            }

    async def get_user_activity_trend(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Получить тренд активности пользователя за указанный период"""
        async with self.db.get_uow() as uow:
            conversations = await uow.conversations.find_by_user_id(user_id)

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            daily_activity = {}
            for conv in conversations:
                if start_date <= conv.created_at <= end_date:
                    date_str = conv.created_at.strftime('%Y-%m-%d')
                    daily_activity[date_str] = daily_activity.get(date_str, 0) + 1

            # Заполняем пропущенные дни нулями
            for i in range(days + 1):
                date_str = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                if date_str not in daily_activity:
                    daily_activity[date_str] = 0

            sorted_activity = dict(sorted(daily_activity.items()))

            return {
                "period_days": days,
                "total_consultations": sum(daily_activity.values()),
                "daily_activity": sorted_activity,
                "most_active_day": max(sorted_activity.items(), key=lambda x: x[1]) if sorted_activity else None,
                "average_per_day": sum(sorted_activity.values()) / len(sorted_activity) if sorted_activity else 0
            }

