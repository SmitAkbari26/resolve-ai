"""
Resolve AI - Embedding Generator
Generates vector embeddings using Sentence Transformers or OpenAI.
"""
from config import  EMBEDDING_MODEL
from utils.logger import get_logger

logger = get_logger(__name__)

_model = None


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


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    Uses the configured provider (sentence_transformers or openai).
    """
    if not texts:
        return []
    return _generate_st_embeddings(texts)


def generate_embedding(text: str) -> list[float]:
    """Generate a single embedding vector."""
    embeddings = generate_embeddings([text])
    return embeddings[0] if embeddings else []


def _generate_st_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Sentence Transformers."""
    model = _get_sentence_transformer()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()
