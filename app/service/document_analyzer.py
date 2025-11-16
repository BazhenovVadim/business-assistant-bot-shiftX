# app/services/document_service.py
from typing import Dict, Any, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession


class DocumentAnalyzer:
    def __init__(self, db):
        self.db = db

    async def create_contract(
            self,
            user_id: int,
            contract_details: str
    ) -> Dict[str, Any]:
        """Генерация договора через ИИ"""

        from app.service.llm_service import LLMService
        llm_service = LLMService()

        prompt = f"""
        Сгенерируй юридический договор на основе следующих деталей:

        {contract_details}

        Верни результат в JSON:
        {{
            "document_type": "договор",
            "title": "название договора",
            "content": "полный текст договора с разделами",
            "key_points": ["ключевой пункт 1", "ключевой пункт 2"],
            "risks": "потенциальные риски",
            "recommendations": "рекомендации по использованию"
        }}
        """

        result = await llm_service.generate_json(prompt)

        # Сохраняем как документ через UoW
        async with self.db.get_uow() as uow:
            # Предполагая, что у вас есть репозиторий документов в UoW
            doc = await uow.documents.create(
                user_id=user_id,
                filename=f"Договор_{uuid.uuid4().hex[:8]}.txt",
                file_type="generated",
                content=result["content"],
                size=len(result["content"])
            )

        return result

    async def create_act(
            self,
            user_id: int,
            act_data: str
    ) -> Dict[str, Any]:
        """Генерация акта через ИИ"""

        from app.service.llm_service import LLMService
        llm_service = LLMService()

        prompt = f"""
        Сгенерируй юридический акт (акт выполненных работ/акт приема-передачи) на основе данных:

        {act_data}

        Верни результат в JSON:
        {{
            "document_type": "акт",
            "title": "название акта", 
            "content": "полный текст акта с реквизитами",
            "required_fields": ["поле 1", "поле 2"],
            "checklist": "чек-лист для заполнения"
        }}
        """

        result = await llm_service.generate_json(prompt)

        async with self.db.get_uow() as uow:
            doc = await uow.documents.create(
                user_id=user_id,
                filename=f"Акт_{uuid.uuid4().hex[:8]}.txt",
                file_type="generated",
                content=result["content"],
                size=len(result["content"])
            )

        return result

    async def check_document(
            self,
            user_id: int,
            document_text: str
    ) -> Dict[str, Any]:
        """Проверка документа на ошибки и риски"""

        from app.service.llm_service import LLMService
        llm_service = LLMService()

        prompt = f"""
        Проверь документ на юридические ошибки, риски и дай рекомендации:

        {document_text}

        Верни результат в JSON:
        {{
            "status": "ok/risky/critical",
            "errors": ["ошибка 1", "ошибка 2"],
            "risks": ["риск 1", "риск 2"],
            "recommendations": ["рекомендация 1", "рекомендация 2"],
            "summary": "общая оценка документа"
        }}
        """

        return await llm_service.generate_json(prompt)


    async def get_user_documents(self, user_id: int) -> list:
        """Получить документы пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.documents.get_user_documents(user_id)