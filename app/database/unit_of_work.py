from sqlalchemy.ext.asyncio import AsyncSession

from .repository.MarketingIdeaRepository import MarketingIdeaRepository
from .repository.UserRepository import UserRepository
from .repository.ConversationRepository import ConversationRepository
from .repository.BusinessDataRepository import BusinessDataRepository
from .repository.TemplateRepository import TemplateRepository
from .repository.QuickActionRepository import QuickActionRepository
from .repository.InsightRepository import InsightRepository
from .repository.DocumentRepository import DocumentRepository
from .repository.ProductRepository import ProductRepository
from .repository.SaleRepository import SaleRepository
from .repository.StockMovementRepository import StockMovementRepository

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
        self.documents = DocumentRepository(self.session)
        self.insights = InsightRepository(self.session)
        self.products = ProductRepository(self.session)
        self.sales = SaleRepository(self.session)
        self.stock_movements = StockMovementRepository(self.session)
        self.marketing_ideas = MarketingIdeaRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()
