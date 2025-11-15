from typing import List, Optional
from app.database.unit_of_work import UnitOfWork
from app.database.models import Template


class TemplateService:
    def __init__(self, db):
        self.db = db

    async def get_templates_by_category(self, category: str) -> List[Template]:
        """Получить шаблоны по категории"""
        async with self.db.get_uow() as uow:
            return await uow.templates.find_by_category(category)

    async def get_all_templates(self) -> List[Template]:
        """Получить все шаблоны"""
        async with self.db.get_uow() as uow:
            return await uow.templates.find_all()

    async def get_legal_templates(self) -> List[Template]:
        """Получить юридические шаблоны"""
        return await self.get_templates_by_category("legal")

    async def get_marketing_templates(self) -> List[Template]:
        """Получить маркетинговые шаблоны"""
        return await self.get_templates_by_category("marketing")

    async def get_document_templates(self) -> List[Template]:
        """Получить шаблоны документов"""
        return await self.get_templates_by_category("documents")

    async def use_template(self, template_id: int) -> None:
        """Увеличить счетчик использования шаблона"""
        async with self.db.get_uow() as uow:
            await uow.templates.increment_usage(template_id)

    async def get_quick_responses(self) -> List[Template]:
        """Получить шаблоны быстрых ответов"""
        return await self.get_templates_by_category("responses")