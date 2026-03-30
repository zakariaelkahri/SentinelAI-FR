# SentinelAI - Copilot Instructions

## Project Summary
SentinelAI is a security platform with:
- Real-time camera stream handling and threat alert ingestion
- A role-protected RAG assistant for security protocols
- Monitoring via Prometheus and Grafana
- Containerized local development through Docker Compose

## Repository Layout
- `sentinel-ai/backend`: FastAPI backend (`app/` package)
- `sentinel-ai/frontend`: React frontend (`react-scripts`)
- `monitoring`: Active Prometheus/Grafana provisioning used by Docker Compose
- `model_training`: YOLO training and RTSP processing scripts
- `.github/workflows`: CI/CD workflows
- `docker-compose.yml`: Root orchestrator for local stack

## Backend Conventions (FastAPI)
- Entry point: `sentinel-ai/backend/app/main.py`
- Routers are included from:
  - `app/api/auth.py`
  - `app/api/users.py`
  - `app/api/predictions.py`
  - `app/api/assistant.py`
  - `app/api/health.py`
- Keep route prefixes and response contracts stable unless explicitly requested.
- Prefer dependency injection (`Depends`) for auth and database access.
- Database session dependency is `app.core.database.get_db` (async SQLAlchemy).

## Auth and Roles
- JWT utilities are in `app/core/security.py`.
- Role checks are implemented with `require_role(...)` in `app/core/auth.py`.
- Current protected flows include admin-managed user operations and assistant access for operator/supervisor roles.

## RAG and Assistant
- Main RAG answering entry point: `app/rag/pipeline.py -> answer_question`.
- Retrieval/LLM config comes from `app/core/config.py`.
- Keep RAG behavior observable: update Prometheus metrics in `app/core/metrics.py` when changing pipeline behavior.
- Avoid introducing hard dependencies in tests on Ollama/Qdrant/MLflow.

## Monitoring and Dashboards
- Runtime Grafana provisioning path is under `monitoring/grafana/provisioning/...`.
- Runtime Prometheus config path is `monitoring/prometheus/prometheus.yml`.
- Docker Compose mounts `monitoring/...` into Grafana/Prometheus containers.
- If dashboard changes do not appear in Grafana, update files in `monitoring/...` first.

## Testing Guidance
- Backend tests live in `sentinel-ai/backend/app/tests`.
- Use `pytest` and FastAPI `TestClient`.
- Prefer deterministic tests with dependency overrides and fakes.
- Do not require live PostgreSQL, Qdrant, Ollama, or external network for unit/integration tests.
- For endpoint integration tests, follow existing `conftest.py` fake session pattern.

## CI/CD Expectations
- Workflow file currently in use: `.github/workflows/ci-cd-security.yml`.
- Quality job runs:
  - `flake8 app --max-line-length=120 --ignore=E501,W503`
- Test job runs:
  - `python -m pytest app/tests -v`
- Docker build job uses:
  - Context: `./sentinel-ai/backend`
  - Dockerfile: `./sentinel-ai/backend/Dockerfile`
- Keep changes compatible with these commands.

## Coding Preferences
- Target Python version: 3.11 for CI.
- Favor clear, typed, maintainable Python over clever shortcuts.
- Keep imports clean and flake8-compliant.
- Avoid dead code, debug prints, and placeholder artifacts in committed code.

## Security and Secrets
- Never hardcode credentials, API keys, or tokens in new code.
- Use environment variables via `app/core/config.py` and `.env`.
- Do not change authentication/authorization behavior silently; document intended impact in PRs.

