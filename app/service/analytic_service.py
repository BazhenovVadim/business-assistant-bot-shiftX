from typing import Dict, Any, List
from app.database.unit_of_work import UnitOfWork
from datetime import datetime, timedelta


class AnalyticService:
    def __init__(self, db):
        self.db = db

    async def get_daily_activity(self, user_id: int) -> Dict[str, Any]:
        """Аналитика ежедневной активности"""
        async with self.db.get_uow() as uow:
            # Консультации за последние 7 дней
            conversations = await uow.conversations.find_by_user_id(user_id, limit=100)

            daily_activity = {}
            for conv in conversations:
                date_str = conv.created_at.strftime('%Y-%m-%d')
                daily_activity[date_str] = daily_activity.get(date_str, 0) + 1

            return {
                "daily_activity": daily_activity,
                "total_last_week": sum(daily_activity.values()),
                "most_active_day": max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
            }

    async def get_category_insights(self, user_id: int) -> Dict[str, Any]:
        """Инсайты по категориям запросов"""
        async with self.db.get_uow() as uow:
            conversations = await uow.conversations.find_by_user_id(user_id, limit=200)

            category_insights = {}
            for conv in conversations:
                category = conv.category or "general"
                if category not in category_insights:
                    category_insights[category] = {
                        "count": 0,
                        "last_used": conv.created_at,
                        "examples": []
                    }

                category_insights[category]["count"] += 1
                category_insights[category]["last_used"] = max(
                    category_insights[category]["last_used"], conv.created_at
                )

                if len(category_insights[category]["examples"]) < 3:
                    category_insights[category]["examples"].append(conv.user_message[:50] + "...")

            return category_insights

    async def generate_weekly_report(self, user_id: int) -> str:
        """Сгенерировать недельный отчет"""
        daily_activity = await self.get_daily_activity(user_id)
        category_insights = await self.get_category_insights(user_id)

        report = "📈 **Недельный отчет по активности:**\n\n"

        report += f"• Всего консультаций: {daily_activity['total_last_week']}\n"

        if daily_activity['most_active_day']:
            day, count = daily_activity['most_active_day']
            report += f"• Самый активный день: {day} ({count} запросов)\n"

        report += "\n**По категориям:**\n"
        for category, insights in list(category_insights.items())[:5]:
            report += f"• {category}: {insights['count']} запросов\n"

        return report