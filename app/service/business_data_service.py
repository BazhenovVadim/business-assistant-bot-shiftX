from typing import List, Optional, Dict, Any
from app.database.unit_of_work import UnitOfWork
from app.database.models import BusinessData


class BusinessDataService:
    def __init__(self, db):
        self.db = db

    async def save_sales_data(self, user_id: int, sales_data: Dict[str, Any]) -> BusinessData:
        """Сохранить данные о продажах"""
        async with self.db.get_uow() as uow:
            business_data = BusinessData(
                user_id=user_id,
                data_type="sales",
                data_json=sales_data,
                period="day"
            )
            return await uow.business_data.save(business_data)

    async def save_inventory_data(self, user_id: int, inventory_data: Dict[str, Any]) -> BusinessData:
        """Сохранить данные об остатках"""
        async with self.db.get_uow() as uow:
            business_data = BusinessData(
                user_id=user_id,
                data_type="inventory",
                data_json=inventory_data,
                period="day"
            )
            return await uow.business_data.save(business_data)

    async def get_latest_sales_report(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить последний отчет по продажам"""
        async with self.db.get_uow() as uow:
            latest_data = await uow.business_data.find_latest_by_type(user_id, "sales")
            return latest_data.data_json if latest_data else None

    async def get_sales_trend(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Получить тренд продаж за период"""
        async with self.db.get_uow() as uow:
            sales_data = await uow.business_data.find_by_user_and_type(user_id, "sales", limit=days)
            return [data.data_json for data in sales_data]

    async def generate_sales_analysis(self, user_id: int) -> str:
        """Сгенерировать анализ продаж"""
        latest_sales = await self.get_latest_sales_report(user_id)

        if not latest_sales:
            return "❌ Данные о продажах не найдены. Добавьте данные через 'анализ продаж'"

        # Простой анализ (потом заменим на AI)
        total_revenue = latest_sales.get('total_revenue', 0)
        avg_check = latest_sales.get('avg_check', 0)
        popular_items = latest_sales.get('popular_items', [])

        analysis = (
            f"📊 **Анализ продаж:**\n\n"
            f"• Общая выручка: {total_revenue:,} руб.\n"
            f"• Средний чек: {avg_check:,} руб.\n"
        )

        if popular_items:
            analysis += "• Популярные товары:\n"
            for item in popular_items[:3]:
                analysis += f"  - {item.get('name')}: {item.get('revenue', 0):,} руб.\n"

        return analysis