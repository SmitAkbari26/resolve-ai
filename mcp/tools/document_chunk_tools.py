from register import register_tool
from clients.document_chunk_client import DocumentChunkClient

document_chunk_client = DocumentChunkClient()

@register_tool(
    name="create_document_chunk",
    description="Create document chunk.",
    input_schema={
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "chunk_index": {"type": "integer"},
            "chunk_text": {"type": "string"},
            "embedding_id": {"type": "string"},
            "metadata_": {"type": "object"},
        },
        "required": ["document_id", "chunk_index", "chunk_text"],
    },
    output_schema={"type": "object"},
)
async def create_document_chunk_tool(**kwargs):
    return await document_chunk_client.create_chunk(
        document_id=kwargs.get("document_id"),
        chunk_index=kwargs.get("chunk_index"),
        chunk_text=kwargs.get("chunk_text"),
        embedding_id=kwargs.get("embedding_id"),
        metadata_=kwargs.get("metadata_", {}),
    )

@register_tool(
    name="get_document_chunk",
    description="Get document chunk.",
    input_schema={
        "type": "object",
        "properties": {"chunk_id": {"type": "string"}},
        "required": ["chunk_id"],
    },
    output_schema={"type": "object"},
)
async def get_document_chunk_tool(**kwargs):
    return await document_chunk_client.get_chunk(chunk_id=kwargs.get("chunk_id"))

@register_tool(
    name="list_document_chunks",
    description="List chunks of a document.",
    input_schema={
        "type": "object",
        "properties": {"document_id": {"type": "string"}},
        "required": ["document_id"],
    },
    output_schema={"type": "object"},
)
async def list_document_chunks_tool(**kwargs):
    return await document_chunk_client.list_chunks(
        document_id=kwargs.get("document_id")
    )

@register_tool(
    name="update_document_chunk",
    description="Update document chunk.",
    input_schema={
        "type": "object",
        "properties": {
            "chunk_id": {"type": "string"},
            "chunk_text": {"type": "string"},
            "embedding_id": {"type": "string"},
            "metadata_": {"type": "object"},
        },
        "required": ["chunk_id"],
    },
    output_schema={"type": "object"},
)
async def update_document_chunk_tool(**kwargs):
    return await document_chunk_client.update_chunk(
        chunk_id=kwargs.get("chunk_id"),
        chunk_text=kwargs.get("chunk_text"),
        embedding_id=kwargs.get("embedding_id"),
        metadata_=kwargs.get("metadata_"),
    )

@register_tool(
    name="delete_document_chunk",
    description="Delete document chunk.",
    input_schema={
        "type": "object",
        "properties": {"chunk_id": {"type": "string"}},
        "required": ["chunk_id"],
    },
    output_schema={"type": "object"},
)
async def delete_document_chunk_tool(**kwargs):
    return await document_chunk_client.delete_chunk(chunk_id=kwargs.get("chunk_id"))