import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from .models import Base
from .unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_url: str = None):

        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not set")
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")

        self.engine = create_async_engine(self.database_url, echo=True)  # echo=True для отладки SQL
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init(self):
        """Создание таблиц в PostgreSQL"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL таблицы созданы успешно")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise

    async def test_connection(self):
        """Тест подключения к PostgreSQL"""
        try:
            async with self.async_session() as session:
                result = await session.execute(text("SELECT version();"))
                version = result.scalar()
                logger.info(f"PostgreSQL подключен: {version}")
                return True
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            return False

    def get_uow(self):
        """Возвращает UnitOfWork (юнит работы) для сервисов"""
        return UnitOfWork(self.async_session)

