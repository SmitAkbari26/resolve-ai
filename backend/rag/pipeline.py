from pathlib import Path
import hashlib

from config import DATASETS_DIR
from rag.document_loader import load_documents
from rag.chunker import chunk_documents
from rag.embeddings import generate_embeddings
from rag.retriever import retrieve, RetrievalResult
from db.vector_store import (
    add_documents,
    collection_count,
    delete_documents_where,
    get_collection,
)
from rag.document_loader import load_file
from utils.logger import get_logger


logger = get_logger(__name__)


class RAGPipeline:
    """
    Orchestrates the full RAG lifecycle:
    1. Ingest documents from datasets directory
    2. Chunk documents into retrievable pieces
    3. Generate embeddings and store in ChromaDB
    4. Retrieve relevant context for user queries
    5. Build context-injected prompts for LLM
    """

    def __init__(self, datasets_dir: Path | None = None):
        self.datasets_dir = datasets_dir or DATASETS_DIR

    def ingest(self, directory: Path | None = None) -> int:
        """
        Ingest documents from a directory into the vector store.
        Returns the number of chunks ingested.
        """
        target_dir = directory or self.datasets_dir
        logger.info(f"Starting document ingestion from: {target_dir}")

        # Step 1: Load documents
        documents = load_documents(target_dir)
        if not documents:
            logger.warning("No documents found for ingestion")
            return 0

        # Step 2: Chunk documents
        chunks = chunk_documents(documents)
        if not chunks:
            logger.warning("No chunks generated")
            return 0

        # Step 3: Generate embeddings
        texts = [chunk.content for chunk in chunks]

        embeddings = generate_embeddings(texts)

        # Step 4: Store in ChromaDB
        ids = [
            hashlib.md5(
                f"{chunk.metadata.get('source', '')}_{chunk.metadata.get('chunk_index', i)}".encode()
            ).hexdigest()
            for i, chunk in enumerate(chunks)
        ]
        metadatas = [chunk.metadata for chunk in chunks]

        add_documents(
            ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings
        )

        logger.info(f"Ingestion complete — {len(chunks)} chunks stored")
        return len(chunks)

    def ingest_file(
        self,
        file_path: Path,
        document_id: str,
        title: str,
        document_type: str,
    ) -> tuple[int, list[dict]]:
        """
        Ingest one uploaded file into ChromaDB.
        Returns (chunk_count, chunk_records for DB).
        """
        path = Path(file_path)
        doc = load_file(path)
        if not doc:
            raise ValueError(f"Could not load or empty file: {path.name}")

        doc.metadata["source"] = title
        doc.metadata["document_id"] = str(document_id)
        doc.metadata["document_type"] = document_type
        doc.metadata["file_name"] = path.name

        chunks = chunk_documents([doc])
        if not chunks:
            raise ValueError("No text chunks generated from file")

        texts = [c.content for c in chunks]
        print(texts)
        embeddings = generate_embeddings(texts)

        ids: list[str] = []
        metadatas: list[dict] = []
        db_chunks: list[dict] = []

        for i, chunk in enumerate(chunks):
            emb_id = f"doc_{document_id}_{i}"
            ids.append(emb_id)
            meta = {
                "source": title,
                "document_id": str(document_id),
                "document_type": document_type,
                "chunk_index": i,
                "type": chunk.metadata.get("type", document_type),
            }
            metadatas.append(meta)
            db_chunks.append(
                {
                    "chunk_index": i,
                    "chunk_text": chunk.content,
                    "embedding_id": emb_id,
                    "metadata_": meta,
                }
            )

        add_documents(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
        logger.info(f"Ingested file {path.name} → {len(chunks)} chunks (doc={document_id})")
        return len(chunks), db_chunks

    def delete_document_vectors(self, document_id: str) -> None:
        """Remove all vector chunks for a knowledge document."""
        delete_documents_where({"document_id": str(document_id)})

    def retrieve_context(
        self, query: str, category: str = "", top_k: int = 5
    ) -> RetrievalResult:
        """
        Retrieve relevant context for a user query.
        Uses hybrid retrieval (vector + knowledge graph).
        """
        return retrieve(query=query, category=category, top_k=top_k)

    def build_augmented_prompt(
        self, query: str, context: RetrievalResult, system_instruction: str = ""
    ) -> str:
        """
        Build a context-augmented prompt for the LLM.
        Injects retrieved context into the prompt template.
        """
        context_text = context.context_text if context else "No relevant context found."

        prompt = f"""You are Resolve AI, an intelligent customer support assistant.
        Use the following retrieved context to answer the customer's query accurately.
        If the context doesn't contain the answer, say so honestly and suggest next steps.

        {system_instruction}

        --- RETRIEVED CONTEXT ---
        {context_text}
        --- END CONTEXT ---

        Customer Query: {query}

        Provide a helpful, accurate, and empathetic response:"""

        return prompt

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        collection = get_collection()
        count = collection_count()
        return {
            "total_chunks": count,
            "datasets_dir": str(self.datasets_dir),
            "collection_name": collection.name if collection else "N/A",
        }
