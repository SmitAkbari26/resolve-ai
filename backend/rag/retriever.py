"""
Resolve AI - Semantic Retriever
Queries ChromaDB for contextually relevant documents, with optional
graph-enhanced retrieval from Neo4j knowledge graph.
"""

from config import RAG_TOP_K
from db.vector_store import query_documents
from rag.embeddings import generate_embedding
from utils.logger import get_logger
from utils.text_sanitize import sanitize_text

logger = get_logger(__name__)


class RetrievalResult:
    """Container for retrieval results from multiple sources."""

    def __init__(self):
        self.vector_results: list[dict] = []
        self.graph_results: list[dict] = []

    @property
    def all_context(self) -> list[dict]:
        """Merge all retrieval results."""
        return self.vector_results + self.graph_results

    @property
    def context_text(self) -> str:
        """Concatenate all context into a single string for LLM injection."""
        parts = []
        for i, result in enumerate(self.all_context, 1):
            source = result.get("source", "Unknown")
            content = sanitize_text(result.get("content", ""))
            parts.append(f"[Source {i}: {source}]\n{content}")
        return "\n\n---\n\n".join(parts)

    def __len__(self):
        return len(self.all_context)


def retrieve(query: str, category: str = "", top_k: int = None) -> RetrievalResult:
    """
    Perform hybrid retrieval: semantic vector search + knowledge graph lookup.

    Args:
        query: The user's query text.
        category: Optional issue category for graph-enhanced retrieval.
        top_k: Number of results to return from vector search.

    Returns:
        RetrievalResult with merged context from all sources.
    """
    top_k = top_k or RAG_TOP_K
    result = RetrievalResult()

    # 1. Semantic Vector Search (ChromaDB)
    try:
        query_emb = generate_embedding(query)
        chroma_results = query_documents(
            query_text=query,
            n_results=top_k,
            query_embedding=query_emb,
        )

        if chroma_results and chroma_results.get("documents"):
            for doc, meta, distance in zip(
                chroma_results["documents"][0],
                chroma_results["metadatas"][0],
                chroma_results["distances"][0],
            ):
                result.vector_results.append(
                    {
                        "content": sanitize_text(doc),
                        "source": meta.get("source", "vector_db"),
                        "type": "vector_search",
                        "relevance_score": 1 - distance,  # cosine distance → similarity
                        "metadata": meta,
                    }
                )
        logger.info(f"Vector search returned {len(result.vector_results)} results")
    except Exception as e:
        logger.warning(f"Vector search failed: {e}")
    return result
