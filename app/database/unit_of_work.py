from sqlalchemy.ext.asyncio import AsyncSession

from .repository.UserRepository import UserRepository
from .repository.ConversationRepository import ConversationRepository
from .repository.BusinessDataRepository import BusinessDataRepository
from .repository.TemplateRepository import TemplateRepository
from .repository.QuickActionRepository import QuickActionRepository


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.conversations = ConversationRepository(self.session)
        self.business_data = BusinessDataRepository(self.session)
        self.templates = TemplateRepository(self.session)
        self.quick_actions = QuickActionRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()
