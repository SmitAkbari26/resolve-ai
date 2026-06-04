"""
Resolve AI - FastAPI Application Entry Point
API Gateway with Auth, Rate Limiting, Request Routing & Logging.
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import API_HOST, API_PORT, API_DEBUG, API_PREFIX, CORS_ORIGINS
from api.user_router import router as user_router
from api.customer_profile_router import router as customer_profile_router
from api.conversation_router import router as conversation_router
from api.conversation_message_router import router as conversation_message_router
from api.ticket_router import router as ticket_router
from api.ticket_comment_router import router as ticket_comment_router
from api.ticket_attachment_router import router as ticket_attachment_router
from api.ticket_history_router import router as ticket_history_router
from api.approval_router import router as approval_router
from api.escalation_router import router as escalation_router
from api.agent_router import router as agent_router
from api.workflow_execution_router import router as workflow_execution_router
from api.workflow_step_router import router as workflow_step_router
from api.knowledge_document_router import router as knowledge_document_router
from api.document_chunk_router import router as document_chunk_router
from api.notification_router import router as notification_router
from api.policy_router import router as policy_router
from api.audit_log_router import router as audit_log_router
from api.chat_router import router as chat_router
from api.widget_configuration_router import router as widget_configuration_router
from api.widget_domain_router import router as widget_domain_router
from api.tenant_router import router as tenant_router
from api.scraper_router import router as scraper_router
from api.middleware.middleware import RequestLoggingMiddleware, RateLimitMiddleware

from db.database import init_db
from db.vector_store import init_vector_store, get_collection
from rag.embeddings import _get_sentence_transformer
from rag.pipeline import RAGPipeline
from utils.logger import get_logger
from mcp.client import mcp_client
from agents.base_agent import BaseAgent

logger = get_logger(__name__)

base_agent = BaseAgent(mcp_client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("Starting Resolve AI Backend...")
    await init_db()
    await mcp_client.start()
    await mcp_client.send_request("initialize")
    init_vector_store()
    _get_sentence_transformer()

    # Perform initial ingestion if collection is empty
    collection = get_collection()
    if collection and collection.count() == 0:
        logger.info("Vector store is empty. Starting initial RAG ingestion...")
        try:
            pipeline = RAGPipeline()
            num_chunks = await pipeline.ingest()
            logger.info(f"Initial ingestion complete: {num_chunks} chunks stored.")
        except Exception as e:
            logger.error(f"Initial RAG ingestion failed: {e}")

    else:
        logger.info(
            f"Vector store already contains {collection.count() if collection else 0} documents."
        )
    logger.info("All services initialized successfully")
    yield
    logger.info("Shutting down Resolve AI Backend...")


app = FastAPI(
    title="Resolve AI",
    description="Agentic Customer Support Resolution System - API Gateway",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cdb7-14-98-189-6.ngrok-free.app",
        "http://localhost:5176",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ─── Routes ──────────────────────────────────────────────
app.include_router(user_router, prefix=f"{API_PREFIX}")
app.include_router(customer_profile_router, prefix=f"{API_PREFIX}")
app.include_router(conversation_router, prefix=f"{API_PREFIX}")
app.include_router(conversation_message_router, prefix=f"{API_PREFIX}")
app.include_router(ticket_router, prefix=f"{API_PREFIX}")
app.include_router(ticket_comment_router, prefix=f"{API_PREFIX}")
app.include_router(ticket_attachment_router, prefix=f"{API_PREFIX}")
app.include_router(ticket_history_router, prefix=f"{API_PREFIX}")
app.include_router(approval_router, prefix=f"{API_PREFIX}")
app.include_router(escalation_router, prefix=f"{API_PREFIX}")
app.include_router(agent_router, prefix=f"{API_PREFIX}")
app.include_router(workflow_execution_router, prefix=f"{API_PREFIX}")
app.include_router(workflow_step_router, prefix=f"{API_PREFIX}")
app.include_router(knowledge_document_router, prefix=f"{API_PREFIX}")
app.include_router(document_chunk_router, prefix=f"{API_PREFIX}")
app.include_router(notification_router, prefix=f"{API_PREFIX}")
app.include_router(policy_router, prefix=f"{API_PREFIX}")
app.include_router(audit_log_router, prefix=f"{API_PREFIX}")
app.include_router(chat_router, prefix=f"{API_PREFIX}")
app.include_router(widget_configuration_router, prefix=f"{API_PREFIX}")
app.include_router(widget_domain_router, prefix=f"{API_PREFIX}")
app.include_router(tenant_router, prefix=f"{API_PREFIX}")
app.include_router(scraper_router, prefix=f"{API_PREFIX}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "resolve-ai-backend"}


@app.get("/test-llm")
async def test_llm():
    return await base_agent.invoke_llm(
        prompt="Can you provide me the the list of the ticket with open status",
        tools_enabled=True,
        allowed_tool_names=["get_ticket", "list_tickets"],
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=API_DEBUG)
