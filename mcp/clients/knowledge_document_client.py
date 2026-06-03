from typing import Optional
from clients.base_client import BaseClient
from config import BASE_URL


class KnowledgeDocumentClient(BaseClient):
    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="knowledge-documents")

    async def create_document(
        self,
        title: str,
        document_type: str,
        source_path: str,
        uploaded_by: str | None = None,
        version: int = 1,
        status: str = "active",
    ):
        payload = {
            "title": title,
            "document_type": document_type,
            "source_path": source_path,
            "uploaded_by": uploaded_by,
            "version": version,
            "status": status,
        }
        return await self.post(payload=payload)

    async def get_document(self, document_id: str):
        return await self.get(path=f"/{document_id}")

    async def list_documents(self, status: Optional[str] = None):
        if status:
            return await self.get(path=f"/status/{status}")
        return await self.get()

    async def get_documents_by_type(self, document_type: str):
        return await self.get(path=f"/type/{document_type}")

    async def update_document(
        self,
        document_id: str,
        title: str | None = None,
        document_type: str | None = None,
        source_path: str | None = None,
        uploaded_by: str | None = None,
        version: int | None = None,
        status: str | None = None,
    ):
        payload = {}
        if title is not None:
            payload["title"] = title
        if document_type is not None:
            payload["document_type"] = document_type
        if source_path is not None:
            payload["source_path"] = source_path
        if uploaded_by is not None:
            payload["uploaded_by"] = uploaded_by
        if version is not None:
            payload["version"] = version
        if status is not None:
            payload["status"] = status
        return await self.put(path=f"/{document_id}", payload=payload)

    async def delete_document(self, document_id: str):
        return await self.delete(path=f"/{document_id}")
