from docx import Document
import PyPDF2
import pytesseract
from PIL import Image

from app.service.llm_service import LLMService


class DocumentAnalyzer:
    def __init__(self, llm: LLMService, doc_repo, insight_repo):
        self.llm = llm
        self.doc_repo = doc_repo
        self.insight_repo = insight_repo

    async def extract_text(self, file_path, file_type):
        if file_type == "pdf":
            reader = PyPDF2.PdfReader(file_path)
            return "\n".join([p.extract_text() for p in reader.pages])

        if file_type == "docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        if file_type in ["jpg", "jpeg", "png"]:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)

        return ""

    async def analyze(self, user_id, file_path, file_type, filename, size):
        text = await self.extract_text(file_path, file_type)

        doc = await self.doc_repo.create(user_id, filename, file_type, text, size)

        insights = await self.llm.generate_json(f"""
            Проанализируй документ:
            {text[:1500]}
        """)

        await self.insight_repo.create(
            doc.id,
            insights["summary"],
            insights["risks"],
            insights["recommendations"],
            str(insights)
        )

        return insights
