# 🤖 Resolve AI — Agentic Customer Support Resolution System

An AI-driven customer support resolution platform powered by **multi-agent orchestration**, **RAG-based knowledge retrieval**, **MCP tool integration**, and **human-in-the-loop approval workflows**.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Streamlit)                    │
│  Chat Interface │ Ticket Dashboard │ Workflow Monitor │ Approvals│
├─────────────────────────────────────────────────────────────────┤
│              API Gateway / Backend (FastAPI)                     │
│        Auth • Rate Limiting • Request Routing • Logging         │
├─────────────────────────────────────────────────────────────────┤
│          Multi-Agent Orchestration Layer (LangGraph)             │
│  1.Conversation → 2.Decision → 3.Ticket                         │
│                  → 4.Approval → 5.Notification                 │
├─────────────────────────────────────────────────────────────────┤
│                  Data & Knowledge Layer                         │
│  ChromaDB │ Neo4j │ PostgreSQL │ Redis │ RAG Pipeline           │
├─────────────────────────────────────────────────────────────────┤
│          MCP Tool Integration Layer (Simulated)                 │
│  Ticket System │ CRM │ KB Search │ Email │ Slack │ Refund       │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
ResolveAI/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Central configuration
│   ├── requirements.txt        # Python dependencies
│   ├── agents/                 # Multi-agent orchestration
│   │   ├── base_agent.py       # Abstract base agent
│   │   ├── conversation_agent.py
│   │   ├── decision_agent.py
│   │   ├── ticket_agent.py
│   │   ├── approval_agent.py
│   │   └── notification_agent.py
│   ├── api/                    # FastAPI route handlers
│   │   ├── middleware.py       # Logging & rate limiting
│   │   ├── routes_chat.py
│   │   ├── routes_tickets.py
│   │   ├── routes_approvals.py
│   │   ├── routes_workflows.py
│   │   ├── routes_rag.py
│   │   └── routes_analytics.py
│   ├── db/                     # Data & knowledge layer
│   │   ├── database.py         # PostgreSQL (SQLAlchemy async)
│   │   ├── schemas.py          # ORM models
│   │   ├── vector_store.py     # ChromaDB vector store
│   │   ├── memory_store.py     # Redis memory/session/cache
│   │   └── knowledge_graph.py  # Neo4j knowledge graph
│   ├── models/                 # Pydantic data models
│   │   ├── ticket.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── approval.py
│   │   ├── workflow.py
│   │   └── agent.py
│   ├── rag/                    # RAG pipeline
│   │   ├── document_loader.py  # Multi-format document loading
│   │   ├── chunker.py          # Document chunking
│   │   ├── embeddings.py       # Embedding generation
│   │   ├── retriever.py        # Hybrid retrieval (vector + graph)
│   │   └── pipeline.py         # End-to-end RAG orchestrator
│   ├── mcp_tools/              # MCP tool integrations (mock)
│   │   ├── base_tool.py        # Abstract MCP tool base
│   │   ├── ticket_system.py    # Mock ticket system
│   │   ├── crm_system.py       # Mock CRM
│   │   ├── knowledge_base.py   # KB search wrapper
│   │   ├── email_service.py    # Mock email
│   │   ├── slack_service.py    # Mock Slack/Teams
│   │   ├── refund_system.py    # Mock refund processing
│   │   └── document_store.py   # Mock document store
│   ├── services/               # Business logic layer
│   │   ├── chat_service.py
│   │   ├── ticket_service.py
│   │   ├── approval_service.py
│   │   ├── notification_service.py
│   │   └── workflow_service.py
│   ├── workflows/              # Workflow orchestration
│   │   ├── state.py            # LangGraph state definition
│   │   └── support_workflow.py # Main workflow engine
│   └── utils/                  # Shared utilities
│       ├── logger.py           # Structured logging with trace IDs
│       └── helpers.py          # Common helper functions
├── frontend/                   # Streamlit UI
│   ├── app.py                  # Main app entry point
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Streamlit pages
│   ├── services/               # API client
│   └── utils/                  # Theme & utilities
├── datasets/                   # RAG knowledge base documents
│   ├── policies/               # Policy documents
│   ├── faqs/                   # FAQ documents
│   └── knowledge_base/         # Product guides
├── docs/                       # Project documentation
└── docker-compose.yml          # Infrastructure services
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL, Redis, Neo4j (or use Docker Compose)
- OpenAI API key or Ollama for local LLM

### 1. Start Infrastructure (Docker)
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Configure your environment
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
uv sync
streamlit run app.py
```

### 4. Ingest Knowledge Base
```bash
curl -X POST http://localhost:8000/api/v1/rag/ingest
```

## 🔑 Key Features

| Feature | Description |
|---------|------------|
| **Context-Aware Conversations** | Maintains conversation memory with sentiment detection |
| **Graph-Augmented RAG** | Hybrid retrieval from ChromaDB vectors + Neo4j knowledge graph |
| **Agentic Workflow Orchestration** | 5-agent pipeline with LangGraph state management |
| **Human-in-the-Loop Approvals** | Workflow pausing for manager review of sensitive actions |
| **MCP Tool Integrations** | Simulated enterprise tools (CRM, Ticketing, Email, Slack) |
| **Real-time Workflow Visualization** | Live agent trace in the Streamlit dashboard |
| **Observability** | Structured logging with trace IDs, performance metrics |

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/send` | Send chat message, triggers full workflow |
| GET | `/api/v1/chat/history/{id}` | Get conversation history |
| GET | `/api/v1/tickets/` | List all tickets |
| POST | `/api/v1/tickets/` | Create a ticket |
| GET | `/api/v1/approvals/pending` | List pending approvals |
| POST | `/api/v1/approvals/{id}/decide` | Approve/reject |
| GET | `/api/v1/workflows/` | List active workflows |
| POST | `/api/v1/rag/ingest` | Ingest documents |
| POST | `/api/v1/rag/query` | Query knowledge base |
| GET | `/api/v1/analytics/dashboard` | Dashboard metrics |

## 📄 License

[MIT License](LICENSE)
