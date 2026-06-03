from sqlalchemy import delete, select
from db.schemas import DocumentChunkRecord
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import KnowledgeDocumentRecord
from schemas.knowledge_document_schema import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
)


class KnowledgeDocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, payload: KnowledgeDocumentCreate):
        document = KnowledgeDocumentRecord(
            title=payload.title,
            document_type=payload.document_type,
            source_path=payload.source_path,
            uploaded_by=payload.uploaded_by,
            version=payload.version,
            status=payload.status,
        )
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_documents(self):
        result = await self.db.execute(select(KnowledgeDocumentRecord))
        return result.scalars().all()

    async def get_document_by_id(self, document_id: str):
        result = await self.db.execute(
            select(KnowledgeDocumentRecord).where(
                KnowledgeDocumentRecord.id == document_id
            )
        )
        return result.scalar_one_or_none()

    async def get_documents_by_type(self, document_type: str):
        result = await self.db.execute(
            select(KnowledgeDocumentRecord).where(
                KnowledgeDocumentRecord.document_type == document_type
            )
        )
        return result.scalars().all()

    async def get_documents_by_status(self, status: str):
        result = await self.db.execute(
            select(KnowledgeDocumentRecord).where(
                KnowledgeDocumentRecord.status == status
            )
        )
        return result.scalars().all()

    async def update_document(
        self, document: KnowledgeDocumentRecord, payload: KnowledgeDocumentUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(document, key, value)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document: KnowledgeDocumentRecord):
        await self.delete_chunks_for_document(str(document.id))
        await self.db.delete(document)
        await self.db.commit()
        return True

    async def delete_chunks_for_document(self, document_id: str):
        await self.db.execute(
            delete(DocumentChunkRecord).where(
                DocumentChunkRecord.document_id == document_id
            )
        )
        await self.db.commit()

    async def count_chunks_for_document(self, document_id: str) -> int:
        result = await self.db.execute(
            select(DocumentChunkRecord).where(
                DocumentChunkRecord.document_id == document_id
            )
        )
        return len(result.scalars().all())
