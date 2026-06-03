from config import (
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    MAX_CHUNK_TOKENS,
    OVERLAP_TOKENS,
    GROQ_MODEL,
)
from rag.document_loader import Document
from utils.logger import get_logger
from transformers import AutoTokenizer

logger = get_logger(__name__)
try:
    tokenizer = AutoTokenizer.from_pretrained(GROQ_MODEL)
except Exception:
    logger.warning(f"Could not load tokenizer for model {GROQ_MODEL}. Falling back to 'gpt2'.")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")


def chunk_document(document: Document) -> list[Document]:
    max_chunk_tokens = MAX_CHUNK_TOKENS
    overlap_tokens = OVERLAP_TOKENS

    text = document.content
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        candidate = (current_chunk + "\n\n" + para).strip()

        if count_tokens(candidate) > max_chunk_tokens and current_chunk:
            chunks.append(current_chunk.strip())

            token_ids = tokenizer.encode(current_chunk, add_special_tokens=False)

            overlap_token_ids = token_ids[-overlap_tokens:]
            overlap_text = tokenizer.decode(overlap_token_ids)

            current_chunk = overlap_text + "\n\n" + para
        else:
            current_chunk = candidate

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    final_chunks = []

    for chunk in chunks:
        if count_tokens(chunk) > max_chunk_tokens * 1.5:
            final_chunks.extend(
                split_by_sentences(chunk, max_chunk_tokens, overlap_tokens)
            )
        else:
            final_chunks.append(chunk)

    chunk_docs = []

    for i, chunk_text in enumerate(final_chunks):
        chunk_meta = {
            **document.metadata,
            "chunk_index": i,
            "total_chunks": len(final_chunks),
            "token_count": count_tokens(chunk_text),
        }

        chunk_docs.append(Document(content=chunk_text, metadata=chunk_meta))
    return chunk_docs


def split_by_sentences(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text by sentences when paragraphs are too long."""
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 > chunk_size and current:
            chunks.append(current.strip())
            overlap = current[-chunk_overlap:] if chunk_overlap > 0 else ""
            current = overlap + " " + sentence
        else:
            current = (current + " " + sentence).strip()

    if current.strip():
        chunks.append(current.strip())

    return chunks


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Chunk a list of documents."""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    logger.info(f"Total chunks generated: {len(all_chunks)}")
    return all_chunks


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))
