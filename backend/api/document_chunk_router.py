from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.document_chunk_service import DocumentChunkService
from schemas.document_chunk_schema import (
    DocumentChunkCreate,
    DocumentChunkUpdate,
    DocumentChunkResponse,
)

router = APIRouter(prefix="/document-chunks", tags=["Document Chunks"])


@router.post("", response_model=DocumentChunkResponse)
async def create_document_chunk_api(
    payload: DocumentChunkCreate, db: AsyncSession = Depends(get_db)
):
    try:
        service = DocumentChunkService(db)
        return await service.create_document_chunk(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[DocumentChunkResponse])
async def get_document_chunks_api(db: AsyncSession = Depends(get_db)):
    service = DocumentChunkService(db)
    return await service.get_document_chunks()


@router.get("/{chunk_id}", response_model=DocumentChunkResponse)
async def get_document_chunk_api(chunk_id: str, db: AsyncSession = Depends(get_db)):
    service = DocumentChunkService(db)
    chunk = await service.get_document_chunk_by_id(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")
    return chunk


@router.get("/document/{document_id}", response_model=list[DocumentChunkResponse])
async def get_chunks_by_document_api(
    document_id: str, db: AsyncSession = Depends(get_db)
):
    service = DocumentChunkService(db)
    return await service.get_chunks_by_document_id(document_id)


@router.get("/embedding/{embedding_id}", response_model=DocumentChunkResponse)
async def get_chunk_by_embedding_api(
    embedding_id: str, db: AsyncSession = Depends(get_db)
):
    service = DocumentChunkService(db)
    chunk = await service.get_chunk_by_embedding_id(embedding_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")
    return chunk


@router.put("/{chunk_id}", response_model=DocumentChunkResponse)
async def update_document_chunk_api(
    chunk_id: str, payload: DocumentChunkUpdate, db: AsyncSession = Depends(get_db)
):
    service = DocumentChunkService(db)
    chunk = await service.update_document_chunk(chunk_id, payload)
    if not chunk:
        raise HTTPException(status_code=404, detail="Document chunk not found")
    return chunk


@router.delete("/{chunk_id}")
async def delete_document_chunk_api(chunk_id: str, db: AsyncSession = Depends(get_db)):
    service = DocumentChunkService(db)
    deleted = await service.delete_document_chunk(chunk_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document chunk not found")
    return {"message": "Document chunk deleted successfully"}
