from clients.base_client import BaseClient
from config import BASE_URL


class DocumentChunkClient(BaseClient):

    def __init__(self):
        super().__init__(base_url=BASE_URL, endpoint="document-chunks")

    async def create_chunk(
        self,
        document_id: str,
        chunk_index: int,
        chunk_text: str,
        embedding_id: str | None = None,
        metadata_: dict = {},
    ):
        payload = {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "embedding_id": embedding_id,
            "metadata_": metadata_,
        }
        return await self.post(payload=payload)

    async def get_chunk(self, chunk_id: str):
        return await self.get(path=f"/{chunk_id}")

    async def list_chunks(self, document_id: str):
        return await self.get(path=f"/document/{document_id}")

    async def update_chunk(
        self,
        chunk_id: str,
        chunk_text: str | None = None,
        embedding_id: str | None = None,
        metadata_: dict | None = None,
    ):
        payload = {}
        if chunk_text is not None:
            payload["chunk_text"] = chunk_text
        if embedding_id is not None:
            payload["embedding_id"] = embedding_id
        if metadata_ is not None:
            payload["metadata_"] = metadata_
        return await self.put(path=f"/{chunk_id}", payload=payload)

    async def delete_chunk(self, chunk_id: str):
        return await self.delete(path=f"/{chunk_id}")
