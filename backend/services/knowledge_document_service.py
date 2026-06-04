from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from config import KNOWLEDGE_UPLOAD_DIR
from rag.pipeline import RAGPipeline
from repositories.knowledge_document_repository import KnowledgeDocumentRepository
from repositories.document_chunk_repository import DocumentChunkRepository
from schemas.knowledge_document_schema import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
)
from schemas.document_chunk_schema import DocumentChunkCreate
from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".md", ".docx", ".txt", ".json"}


def _doc_type_from_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    mapping = {
        ".pdf": "pdf",
        ".md": "markdown",
        ".docx": "docx",
        ".txt": "text",
        ".json": "json",
    }
    return mapping.get(ext, "unknown")


class KnowledgeDocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = KnowledgeDocumentRepository(db)
        self.chunk_repository = DocumentChunkRepository(db)
        self.pipeline = RAGPipeline()

    async def _to_response(self, document) -> KnowledgeDocumentResponse:
        chunk_count = await self.repository.count_chunks_for_document(str(document.id))
        return KnowledgeDocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type,
            source_path=document.source_path,
            tenant_id=document.tenant_id,
            uploaded_by=document.uploaded_by,
            version=document.version,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            chunk_count=chunk_count,
        )

    async def upload_and_ingest(
        self,
        file_content: bytes,
        filename: str,
        title: str | None,
        document_type: str | None,
        uploaded_by: str | None,
        tenant_id: UUID | None = None,
    ) -> tuple[KnowledgeDocumentResponse, int]:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        if not file_content:
            raise ValueError("Uploaded file is empty")

        KNOWLEDGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        doc_id = uuid4()
        safe_name = Path(filename).name.replace(" ", "_")
        stored_name = f"{doc_id}_{safe_name}"
        stored_path = KNOWLEDGE_UPLOAD_DIR / stored_name

        stored_path.write_bytes(file_content)

        title = (title or Path(filename).stem).strip()[:255]
        doc_type = (document_type or _doc_type_from_filename(filename)).strip()[:100]

        db_doc = await self.repository.create_document(
            KnowledgeDocumentCreate(
                title=title,
                document_type=doc_type,
                source_path=str(stored_path),
                tenant_id=tenant_id,
                uploaded_by=uploaded_by,
                status="active",
            )
        )

        try:
            chunk_count, chunk_rows = await self.pipeline.ingest_file(
                file_path=stored_path,
                document_id=str(db_doc.id),
                title=title,
                document_type=doc_type,
                tenant_id=tenant_id,
            )

            for row in chunk_rows:
                await self.chunk_repository.create_document_chunk(
                    DocumentChunkCreate(
                        document_id=db_doc.id,
                        chunk_index=row["chunk_index"],
                        chunk_text=row["chunk_text"],
                        embedding_id=row["embedding_id"],
                        metadata_=row["metadata_"],
                    )
                )

        except Exception as e:
            await self.repository.delete_chunks_for_document(str(db_doc.id))
            await self.repository.delete_document(db_doc)
            if stored_path.exists():
                stored_path.unlink()
            raise ValueError(f"Ingestion failed: {e}") from e

        return await self._to_response(db_doc), chunk_count

    async def reingest_document(self, document_id: str) -> int:
        document = await self.repository.get_document_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        path = Path(document.source_path)
        if not path.exists():
            raise ValueError("Source file missing on disk")

        self.pipeline.delete_document_vectors(str(document.id))
        await self.repository.delete_chunks_for_document(str(document.id))

        chunk_count, chunk_rows = await self.pipeline.ingest_file(
            file_path=path,
            document_id=str(document.id),
            title=document.title,
            document_type=document.document_type,
        )

        for row in chunk_rows:
            await self.chunk_repository.create_document_chunk(
                DocumentChunkCreate(
                    document_id=document.id,
                    chunk_index=row["chunk_index"],
                    chunk_text=row["chunk_text"],
                    embedding_id=row["embedding_id"],
                    metadata_=row["metadata_"],
                )
            )

        return chunk_count


    async def get_stats(self) -> dict:
        from db.vector_store import collection_count

        documents = await self.repository.get_documents()
        stats = self.pipeline.get_stats()
        return {
            "total_vector_chunks": collection_count(),
            "total_documents": len(documents),
            "collection_name": stats["collection_name"],
            "upload_directory": str(KNOWLEDGE_UPLOAD_DIR),
        }

    async def create_document(self, payload: KnowledgeDocumentCreate):
        doc = await self.repository.create_document(payload)
        return await self._to_response(doc)

    async def get_documents(self):
        docs = await self.repository.get_documents()
        return [await self._to_response(d) for d in docs]

    async def get_document_by_id(self, document_id: str):
        document = await self.repository.get_document_by_id(document_id)
        if not document:
            return None
        return await self._to_response(document)

    async def get_documents_by_type(self, document_type: str):
        docs = await self.repository.get_documents_by_type(document_type)
        return [await self._to_response(d) for d in docs]

    async def get_documents_by_status(self, status: str):
        docs = await self.repository.get_documents_by_status(status)
        return [await self._to_response(d) for d in docs]

    async def update_document(self, document_id: str, payload: KnowledgeDocumentUpdate):
        document = await self.repository.get_document_by_id(document_id)
        if not document:
            return None
        updated = await self.repository.update_document(document, payload)
        return await self._to_response(updated)

    async def delete_document(self, document_id: str) -> bool:
        document = await self.repository.get_document_by_id(document_id)
        if not document:
            return False

        self.pipeline.delete_document_vectors(str(document.id))

        path = Path(document.source_path)
        if path.exists():
            try:
                path.unlink()
            except OSError as e:
                logger.warning(f"Could not delete file {path}: {e}")

        await self.repository.delete_document(document)
        return True

    async def ingest_datasets_folder(self) -> int:
        """Re-ingest static files from datasets/ (legacy behavior)."""
        return await self.pipeline.ingest()

