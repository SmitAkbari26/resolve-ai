"""
Resolve AI - Central Configuration
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
KNOWLEDGE_UPLOAD_DIR = BASE_DIR / "data" / "uploads" / "knowledge"

# ─── FastAPI ─────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"
API_PREFIX = "/api/v1"
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173, http://localhost:5175, http://localhost:5174, http://localhost:5176,http://localhost:3000",
).split(",")

# ─── LLM ─────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # openai | ollama | groq
GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY", "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"
)
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# ─── Embeddings ──────────────────────────────────────────
EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER", "sentence_transformers"
)  # sentence_transformers | openai
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ─── PostgreSQL ──────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "resolve_ai")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "resolve_ai_pass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "resolve_ai")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

# ─── ChromaDB ────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "resolve_ai_kb")

# ─── Redis ───────────────────────────────────────────────
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# ─── Neo4j (Knowledge Graph) ────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "resolve_ai_graph")

# ─── RAG Settings ────────────────────────────────────────
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1024"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "128"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MAX_CHUNK_TOKENS = 400
OVERLAP_TOKENS = 80

# ─── Workflow Settings ───────────────────────────────────
APPROVAL_REFUND_THRESHOLD = float(os.getenv("APPROVAL_REFUND_THRESHOLD", "100.0"))
MAX_AUTO_RESOLVE_SEVERITY = os.getenv("MAX_AUTO_RESOLVE_SEVERITY", "medium")

# ─── Notification ────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# ─── Logging ─────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── MCP ─────────────────────────────────────────────
MCP_SERVER_BASE_URL = os.getenv("MCP_SERVER_BASE_URL", "http://localhost:9000")
