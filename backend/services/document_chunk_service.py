from sqlalchemy.ext.asyncio import AsyncSession
from repositories.document_chunk_repository import DocumentChunkRepository
from schemas.document_chunk_schema import DocumentChunkCreate, DocumentChunkUpdate


class DocumentChunkService:
    def __init__(self, db: AsyncSession):

        self.repository = DocumentChunkRepository(db)

    async def create_document_chunk(self, payload: DocumentChunkCreate):
        return await self.repository.create_document_chunk(payload)

    async def get_document_chunks(self):
        return await self.repository.get_document_chunks()

    async def get_document_chunk_by_id(self, chunk_id: str):
        return await self.repository.get_document_chunk_by_id(chunk_id)

    async def get_chunks_by_document_id(self, document_id: str):
        return await self.repository.get_chunks_by_document_id(document_id)

    async def get_chunk_by_embedding_id(self, embedding_id: str):
        return await self.repository.get_chunk_by_embedding_id(embedding_id)

    async def update_document_chunk(self, chunk_id: str, payload: DocumentChunkUpdate):
        chunk = await self.repository.get_document_chunk_by_id(chunk_id)
        if not chunk:
            return None
        return await self.repository.update_document_chunk(chunk, payload)

    async def delete_document_chunk(self, chunk_id: str):
        chunk = await self.repository.get_document_chunk_by_id(chunk_id)
        if not chunk:
            return False
        return await self.repository.delete_document_chunk(chunk)
