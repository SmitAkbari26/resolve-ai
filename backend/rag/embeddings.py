"""
Resolve AI - Embedding Generator
Generates vector embeddings using Sentence Transformers or OpenAI.
"""
from config import  EMBEDDING_MODEL
from utils.logger import get_logger

logger = get_logger(__name__)

_model = None


import asyncio

def _get_sentence_transformer():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info(f"Sentence Transformer model loaded: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _model


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts asynchronously.
    Uses sentence_transformers offloaded to a thread pool.
    """
    if not texts:
        return []
    return await asyncio.to_thread(_generate_st_embeddings, texts)


async def generate_embedding(text: str) -> list[float]:
    """Generate a single embedding vector asynchronously."""
    embeddings = await generate_embeddings([text])
    return embeddings[0] if embeddings else []


def _generate_st_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Sentence Transformers (blocking CPU work)."""
    model = _get_sentence_transformer()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()

