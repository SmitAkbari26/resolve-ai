"""
Resolve AI - ChromaDB Vector Store
Stores document embeddings for RAG semantic retrieval.
"""

import chromadb
from chromadb.config import Settings

from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from utils.logger import get_logger

logger = get_logger(__name__)

_client: chromadb.ClientAPI | None = None
_collection = None


def init_vector_store():
    """Initialize the ChromaDB persistent client and collection."""
    global _client, _collection
    try:
        _client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB initialized — collection '{CHROMA_COLLECTION_NAME}' "
            f"({_collection.count()} documents)"
        )
    except Exception as e:
        logger.warning(
            f"ChromaDB initialization failed (continuing without vector store): {e}"
        )


def get_collection():
    """Return the active ChromaDB collection."""
    if _collection is None:
        init_vector_store()
    return _collection


def add_documents(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
    embeddings: list[list[float]] | None = None,
):
    """Add documents (with optional pre-computed embeddings) to the vector store."""
    collection = get_collection()
    if collection is None:
        logger.error("ChromaDB collection not available")
        return

    kwargs = {"ids": ids, "documents": documents, "metadatas": metadatas}
    if embeddings:
        kwargs["embeddings"] = embeddings

    collection.upsert(**kwargs)
    logger.info(f"Upserted {len(ids)} documents into ChromaDB")


def query_documents(
    query_text: str,
    n_results: int = 5,
    where: dict | None = None,
    query_embedding: list[float] | None = None,
) -> dict:
    """Query the vector store for semantically similar documents."""
    collection = get_collection()
    if collection is None:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    kwargs = {"n_results": n_results}
    if query_embedding:
        kwargs["query_embeddings"] = [query_embedding]
    else:
        kwargs["query_texts"] = [query_text]
    if where:
        kwargs["where"] = where

    return collection.query(**kwargs)


def delete_documents(ids: list[str]):
    """Delete documents by ID from the vector store."""
    collection = get_collection()
    if collection and ids:
        collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from ChromaDB")


def delete_documents_where(where: dict):
    """Delete documents matching metadata filter (e.g. document_id)."""
    collection = get_collection()
    if collection and where:
        collection.delete(where=where)
        logger.info(f"Deleted ChromaDB documents where {where}")


def collection_count() -> int:
    collection = get_collection()
    return collection.count() if collection else 0
