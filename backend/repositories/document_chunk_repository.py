from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.schemas import DocumentChunkRecord
from schemas.document_chunk_schema import DocumentChunkCreate, DocumentChunkUpdate


class DocumentChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document_chunk(self, payload: DocumentChunkCreate):
        chunk = DocumentChunkRecord(
            document_id=payload.document_id,
            chunk_index=payload.chunk_index,
            chunk_text=payload.chunk_text,
            embedding_id=payload.embedding_id,
            metadata_=payload.metadata_,
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def get_document_chunks(self):
        result = await self.db.execute(select(DocumentChunkRecord))
        return result.scalars().all()

    async def get_document_chunk_by_id(self, chunk_id: str):
        result = await self.db.execute(
            select(DocumentChunkRecord).where(DocumentChunkRecord.id == chunk_id)
        )
        return result.scalar_one_or_none()

    async def get_chunks_by_document_id(self, document_id: str):
        result = await self.db.execute(
            select(DocumentChunkRecord).where(
                DocumentChunkRecord.document_id == document_id
            )
        )
        return result.scalars().all()

    async def get_chunk_by_embedding_id(self, embedding_id: str):
        result = await self.db.execute(
            select(DocumentChunkRecord).where(
                DocumentChunkRecord.embedding_id == embedding_id
            )
        )
        return result.scalar_one_or_none()

    async def update_document_chunk(
        self, chunk: DocumentChunkRecord, payload: DocumentChunkUpdate
    ):
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(chunk, key, value)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def delete_document_chunk(self, chunk: DocumentChunkRecord):
        await self.db.delete(chunk)
        await self.db.commit()
        return True
