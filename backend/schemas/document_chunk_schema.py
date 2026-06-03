from uuid import UUID
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class DocumentChunkCreate(BaseModel):
    document_id: UUID
    chunk_index: int
    chunk_text: str
    embedding_id: str | None = None
    metadata_: dict[str, Any] = {}


class DocumentChunkUpdate(BaseModel):
    chunk_index: int | None = None
    chunk_text: str | None = None
    embedding_id: str | None = None
    metadata_: dict[str, Any] | None = None


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    chunk_text: str
    embedding_id: str | None
    metadata_: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
