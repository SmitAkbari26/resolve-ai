from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from services.knowledge_document_service import KnowledgeDocumentService
from schemas.knowledge_document_schema import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentUploadResponse,
    KnowledgeBaseStatsResponse,
)
from core.security import require_role

router = APIRouter(prefix="/knowledge-documents", tags=["Knowledge Documents"])

# ─── Static paths (must stay before /{document_id}) ─────────────────────────

@router.get("/meta/stats", response_model=KnowledgeBaseStatsResponse)
async def knowledge_base_stats_api(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager", "agent"])),
):
    service = KnowledgeDocumentService(db)
    return await service.get_stats()


@router.post("/upload", response_model=KnowledgeDocumentUploadResponse)
async def upload_document_api(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    document_type: str | None = Form(None),
    uploaded_by: str | None = Form(None),
    tenant_id: UUID | None = Form(None),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    """
    Upload a file, store it on disk, index chunks in ChromaDB for RAG.
    Supported: .pdf, .md, .docx, .txt, .json
    """
    try:
        content = await file.read()
        filename = file.filename or "document.txt"
        service = KnowledgeDocumentService(db)
        document, chunks = await service.upload_and_ingest(
            file_content=content,
            filename=filename,
            title=title,
            document_type=document_type,
            uploaded_by=uploaded_by,
            tenant_id=tenant_id,
        )
        return KnowledgeDocumentUploadResponse(
            document=document,
            chunks_ingested=chunks,
            message=f"Uploaded and indexed {chunks} chunks.",
        )
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/ingest")
async def ingest_datasets_api(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    """Re-ingest all files from the static datasets/ folder."""
    try:
        service = KnowledgeDocumentService(db)
        count = await service.ingest_datasets_folder()
        return {"message": "Ingestion successful", "chunks_ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[KnowledgeDocumentResponse])
async def get_documents_api(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager", "agent"])),
):
    service = KnowledgeDocumentService(db)
    return await service.get_documents()


@router.post("", response_model=KnowledgeDocumentResponse)
async def create_document_api(
    payload: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    try:
        service = KnowledgeDocumentService(db)
        return await service.create_document(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("/by-type/{document_type}", response_model=list[KnowledgeDocumentResponse])
async def get_documents_by_type_api(
    document_type: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager", "agent"])),
):
    service = KnowledgeDocumentService(db)
    return await service.get_documents_by_type(document_type)


@router.get("/by-status/{status}", response_model=list[KnowledgeDocumentResponse])
async def get_documents_by_status_api(
    status: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager", "agent"])),
):
    service = KnowledgeDocumentService(db)
    return await service.get_documents_by_status(status)


# ─── Document ID routes (UUID avoids matching "stats", "type", etc.) ────────

@router.get("/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document_api(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin", "manager", "agent"])),
):
    service = KnowledgeDocumentService(db)
    document = await service.get_document_by_id(str(document_id))
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge document not found")
    return document


@router.put("/{document_id}", response_model=KnowledgeDocumentResponse)
async def update_document_api(
    document_id: UUID,
    payload: KnowledgeDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = KnowledgeDocumentService(db)
    document = await service.update_document(str(document_id), payload)
    if not document:
        raise HTTPException(status_code=404, detail="Knowledge document not found")
    return document


@router.delete("/{document_id}")
async def delete_document_api(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    service = KnowledgeDocumentService(db)
    deleted = await service.delete_document(str(document_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Knowledge document not found")
    return {"message": "Knowledge document and RAG vectors deleted successfully"}


@router.post("/{document_id}/reingest")
async def reingest_document_api(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role(["admin"])),
):
    try:
        service = KnowledgeDocumentService(db)
        count = await service.reingest_document(str(document_id))
        return {"message": "Re-indexed successfully", "chunks_ingested": count}
    except ValueError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
