# app/core/di.py
from aiogram import BaseMiddleware
from app.database import Database
from app.service import UserService, ConversationService, AnalyticService, WarehouseService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self):
        self.db = None

    async def __call__(self, handler, event, data):
        if self.db is None:
            self.db = Database()
            await self.db.init()

        # Создаем сервисы
        data["user_service"] = UserService(self.db)
        data["conversation_service"] = ConversationService(self.db)
        data["analytic_service"] = AnalyticService(self.db)
        data["warehouse_service"] = WarehouseService(self.db)

        return await handler(event, data)