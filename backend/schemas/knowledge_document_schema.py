from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class KnowledgeDocumentCreate(BaseModel):
    title: str
    document_type: str
    source_path: str
    uploaded_by: str | None = None
    version: int = 1
    status: str = "active"


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = None
    document_type: str | None = None
    source_path: str | None = None
    uploaded_by: str | None = None
    version: int | None = None
    status: str | None = None


class KnowledgeDocumentResponse(BaseModel):
    id: UUID
    title: str
    document_type: str
    source_path: str
    uploaded_by: str | None
    version: int
    status: str
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    class Config:
        from_attributes = True


class KnowledgeDocumentUploadResponse(BaseModel):
    document: KnowledgeDocumentResponse
    chunks_ingested: int
    message: str


class KnowledgeBaseStatsResponse(BaseModel):
    total_vector_chunks: int
    total_documents: int
    collection_name: str
    upload_directory: str
