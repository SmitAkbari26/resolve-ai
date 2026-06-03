from register import register_tool
from clients.knowledge_document_client import KnowledgeDocumentClient

knowledge_document_client = KnowledgeDocumentClient()


@register_tool(
    name="create_knowledge_document",
    description="Create a knowledge document.",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "document_type": {"type": "string"},
            "source_path": {"type": "string"},
            "uploaded_by": {"type": "string"},
            "version": {"type": "integer"},
            "status": {"type": "string"},
        },
        "required": ["title", "document_type", "source_path"],
    },
    output_schema={"type": "object"},
)
async def create_knowledge_document_tool(**kwargs):
    return await knowledge_document_client.create_document(
        title=kwargs.get("title"),
        document_type=kwargs.get("document_type"),
        source_path=kwargs.get("source_path"),
        uploaded_by=kwargs.get("uploaded_by"),
        version=kwargs.get("version", 1),
        status=kwargs.get("status", "active"),
    )


@register_tool(
    name="get_knowledge_document",
    description="Get knowledge document details.",
    input_schema={
        "type": "object",
        "properties": {"document_id": {"type": "string"}},
        "required": ["document_id"],
    },
    output_schema={"type": "object"},
)
async def get_knowledge_document_tool(**kwargs):
    return await knowledge_document_client.get_document(
        document_id=kwargs.get("document_id")
    )


@register_tool(
    name="list_knowledge_documents",
    description="List knowledge documents.",
    input_schema={"type": "object", "properties": {"status": {"type": "string"}}},
    output_schema={"type": "object"},
)
async def list_knowledge_documents_tool(**kwargs):
    return await knowledge_document_client.list_documents(status=kwargs.get("status"))


@register_tool(
    name="get_knowledge_documents_by_type",
    description="Get documents by type.",
    input_schema={
        "type": "object",
        "properties": {"document_type": {"type": "string"}},
        "required": ["document_type"],
    },
    output_schema={"type": "object"},
)
async def get_knowledge_documents_by_type_tool(**kwargs):
    return await knowledge_document_client.get_documents_by_type(
        document_type=kwargs.get("document_type")
    )


@register_tool(
    name="update_knowledge_document",
    description="Update knowledge document.",
    input_schema={
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "title": {"type": "string"},
            "document_type": {"type": "string"},
            "source_path": {"type": "string"},
            "uploaded_by": {"type": "string"},
            "version": {"type": "integer"},
            "status": {"type": "string"},
        },
        "required": ["document_id"],
    },
    output_schema={"type": "object"},
)
async def update_knowledge_document_tool(**kwargs):
    return await knowledge_document_client.update_document(
        document_id=kwargs.get("document_id"),
        title=kwargs.get("title"),
        document_type=kwargs.get("document_type"),
        source_path=kwargs.get("source_path"),
        uploaded_by=kwargs.get("uploaded_by"),
        version=kwargs.get("version"),
        status=kwargs.get("status"),
    )


@register_tool(
    name="delete_knowledge_document",
    description="Delete knowledge document.",
    input_schema={
        "type": "object",
        "properties": {"document_id": {"type": "string"}},
        "required": ["document_id"],
    },
    output_schema={"type": "object"},
)
async def delete_knowledge_document_tool(**kwargs):
    return await knowledge_document_client.delete_document(
        document_id=kwargs.get("document_id")
    )
