# app/core/dependencies.py
from fastapi import Depends

from app.database import Database, UnitOfWork
from app.database.repository import (
    UserRepository,
    ConversationRepository,
    DocumentRepository,
    InsightRepository
)
from app.service import WarehouseService, MarketingService
from app.service.user_service import UserService
from app.service.conversation_service import ConversationService
from app.service.analytic_service import AnalyticService
from app.service.document_analyzer import DocumentAnalyzer
from app.service.llm_service import LLMService


async def get_db() -> Database:
    """Возвращает экземпляр базы данных"""
    db = Database()
    await db.init()
    return db


async def get_uow(db: Database = Depends(get_db)) -> UnitOfWork:
    """Возвращает Unit of Work"""
    return db.get_uow()


async def get_user_repository(uow: UnitOfWork = Depends(get_uow)) -> UserRepository:
    return uow.users


async def get_conversation_repository(uow: UnitOfWork = Depends(get_uow)) -> ConversationRepository:
    return uow.conversations


async def get_document_repository(uow: UnitOfWork = Depends(get_uow)) -> DocumentRepository:
    return uow.documents


async def get_insight_repository(uow: UnitOfWork = Depends(get_uow)) -> InsightRepository:
    return uow.insights


async def get_llm_service() -> LLMService:
    """Возвращает LLM сервис"""
    return LLMService()  # добавь конфигурацию если нужно


async def get_user_service(db: Database = Depends(get_db)) -> UserService:
    return UserService(db)


async def get_conversation_service(db: Database = Depends(get_db)) -> ConversationService:
    return ConversationService(db)


async def get_analytic_service(db: Database = Depends(get_db)) -> AnalyticService:
    return AnalyticService(db)


async def get_warehouse_service(db: Database = Depends(get_db)) -> WarehouseService:
    return WarehouseService(db)


async def get_marketing_service(db: Database = Depends(get_db)) -> MarketingService:
    return MarketingService(db)


async def get_document_service(
        db: Database = Depends(get_db)) -> DocumentAnalyzer:
    return DocumentAnalyzer(db)
