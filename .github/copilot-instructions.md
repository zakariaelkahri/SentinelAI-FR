# CliniQ — Copilot Instructions

## Architecture Overview

CliniQ is a **medical clinical-decision-support** app using RAG (Retrieval-Augmented Generation) over a French medical protocol manual. The stack is fully Dockerized:

| Layer | Tech | Entry point |
|---|---|---|
| **API** | FastAPI (async, Python 3.11) | `app/main.py` — mounts routes under `/api/v1` |
| **RAG pipeline** | LangChain + Ollama (mistral-nemo) + Qdrant | `app/rag/pipeline.py` → `answer_question()` |
| **DB** | PostgreSQL 16 via async SQLAlchemy | `app/db/session.py` (async engine) |
| **Frontend** | React 18 + Vite + Tailwind CSS 4 | `frontend/src/App.jsx` |
| **Monitoring** | Prometheus + Grafana + MLflow | `app/core/metrics.py`, `monitoring/` |

### Data Flow

1. User sends question → `POST /api/v1/query/assistant` (JWT-protected)
2. Route runs `answer_question()` in a thread (`asyncio.to_thread`) to avoid blocking the async event loop
3. RAG pipeline: **Qdrant retriever** (top-20) → **cross-encoder reranker** (BAAI/bge-reranker-base, top-5) → **LLM** (mistral-nemo via Ollama, temp=0)
4. Answer + question persisted to `queries` table, returned to frontend

### Key Knowledge Source

The single source document is `data/processed/Guide-des-Protocoles.md` (French medical protocols). It is loaded at import time in `app/rag/loader.py`, chunked with a hybrid strategy (Markdown header splitting → recursive character splitting, 800/150) in `app/rag/chunking.py`, then embedded via HuggingFace embeddings into a Qdrant collection named `medical_manual`.

## Project Conventions

### Backend (`app/`)

- **Config**: All settings via `pydantic-settings` in `app/core/config.py`; env vars from `.env`. Required keys: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `EMBEDDING_MODEL`, `LLAMA_KEY`, `GEMINI_KEY`, `QDRANT_URL`, `DATABASE_URL`.
- **Auth**: JWT-based (`python-jose`). Passwords hashed with bcrypt via `app/core/security.py`. Token carries user `id` as subject. Dependency `get_current_user_id` in `app/api/deps.py` extracts the user ID from the token.
- **DB models** use SQLAlchemy declarative base (`app/db/base.py`). Tables auto-created on startup via `lifespan` in `main.py`. Two models: `User` and `Query` (in `app/models/`).
- **Schemas** (Pydantic v2) live in `app/schemas/`; use `from_attributes = True` for ORM ↔ response conversion.
- **Services** in `app/services/` contain business logic (queries to DB). Routes in `app/api/routes/` are thin wrappers.
- **Metrics**: Every RAG call and HTTP endpoint increments Prometheus counters/histograms defined in `app/core/metrics.py`. Exposed at `GET /metrics`.
- **MLflow logging** is pervasive across RAG modules (`chunking`, `embeddings`, `retriever`, `llm`, `pipeline`). Each logs params/metrics inside try/except so MLflow failures are silent.

### Frontend (`frontend/`)

- React SPA with client-side routing (`react-router-dom`). Protected routes check `localStorage.access_token`.
- API calls go through `frontend/src/services/api.js` (Axios instance with `/api/v1` base, auto-attaches Bearer token, redirects to `/login` on 401).
- Styling: Tailwind CSS 4 (via `@tailwindcss/vite` plugin). No separate config file needed.

### Tests (`app/tests/`)

- Tests use `pytest`. Current tests are **unit tests with fakes/mocks** — no live services needed.
- Pattern: define `Fake*` classes mimicking LangChain objects (e.g., `FakeDocument`, `FakeAIMessage`) and test interface contracts.
- Run: `pytest app/tests/`

## Docker & Dev Workflow

- **Start everything**: `docker compose up --build`
- Services: `api` (:8004), `postgres` (:5432), `qdrant` (:6333), `ollama` (:11434), `front` (:3000), `mlflow` (:5000), `prometheus` (:9090), `grafana` (:3001), `pgadmin` (:5050), `cadvisor` (:8081)
- The API container sets `PYTHONPATH=/workspace` and mounts `./app` and `./data` as volumes for hot-reload (`--reload` flag in entrypoint).
- **Rebuild vector store**: Run `app/rag/vectorstore.py` directly — it deletes and recreates the `medical_manual` Qdrant collection from the processed markdown.
- **Seed database**: `python -m app.seeders.seed` (seeds users first, then queries).
- **Evaluate RAG**: `app/rag/evaluation.py` has built-in French medical test cases with precision@k, recall@k, and LLM-based relevance scoring.

## Important Patterns

- The RAG prompt in `app/rag/prompt.py` enforces **language-matching** (respond in the user's question language) and **strict context-grounding** (no hallucination). The AI persona is "ProtoCare AI". Do not change these safety rules without explicit request.
- Docker hostnames (`postgres`, `qdrant`, `ollama`, `mlflow`) are used for inter-service communication. When running outside Docker, override `QDRANT_URL`, `DATABASE_URL`, etc.
- Ollama requires an NVIDIA GPU (`deploy.resources.reservations.devices` in compose).
- The embedding model is configured via `EMBEDDING_MODEL` env var (HuggingFace model name).
