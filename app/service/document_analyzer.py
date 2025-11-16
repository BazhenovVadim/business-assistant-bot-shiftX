import os

import aiofiles
import pdfplumber
from docx import Document

from app.service.llm_service import LLMService


class DocumentAnalyzer:
    def __init__(self, llm: LLMService, document_repository, insight_repository):
        self.llm = llm
        self.document_repository = document_repository
        self.insight_repository = insight_repository

    async def _extract_from_pdf(self, file_path: str) -> str:
        """Извлечение текста из PDF"""
        try:
            text = ""
            async with aiofiles.tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, "temp.pdf")
                async with aiofiles.open(file_path, 'rb') as source:
                    async with aiofiles.open(temp_path, 'wb') as target:
                        await target.write(await source.read())

                with pdfplumber.open(temp_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Ошибка извлечения из PDF: {str(e)}")

    async def _extract_from_docx(self, file_path: str) -> str:
        """Извлечение текста из DOCX"""
        try:
            text = ""
            async with aiofiles.tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, "temp.docx")
                async with aiofiles.open(file_path, 'rb') as source:
                    async with aiofiles.open(temp_path, 'wb') as target:
                        await target.write(await source.read())


                doc = Document(temp_path)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Ошибка извлечения из DOCX: {str(e)}")

    async def extract_text(self, file_path: str, file_type: str) -> str:
        """Извлечение текста из файла"""
        if file_type == 'pdf':
            return await self._extract_from_pdf(file_path)
        elif file_type == 'docx':
            return await self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    async def analyze(self, user_id, file_path, file_type, filename, size):
        text = await self.extract_text(file_path, file_type)

        doc = await self.document_repository.create(user_id, filename, file_type, text, size)

        # Анализируем через ИИ
        insights = await self.llm.generate_json(f"""
            Проанализируй документ и верни JSON:
            {{
                "summary": "краткое содержание",
                "risks": "выявленные риски", 
                "recommendations": "рекомендации"
            }}

            Текст документа:
            {text[:1500]}
        """)

        await self.insight_repository.create(
            doc.id,
            insights["summary"],
            insights["risks"],
            insights["recommendations"],
            str(insights)
        )

        return insights