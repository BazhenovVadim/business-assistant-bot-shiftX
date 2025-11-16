# app/repositories/document_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Document, Insight
from sqlalchemy import select


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            user_id: int,
            filename: str,
            file_type: str,
            content: str,
            size: int
    ) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            content=content,
            size=size
        )
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: int) -> Document:
        result = await self.session.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_user_documents(self, user_id: int) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.user_id == user_id)
        )
        return result.scalars().all()

