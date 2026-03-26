from pathlib import Path

from langchain_community.document_loaders import TextLoader

from app.core.config import settings

# /app/rag/loader.py -> /app
BASE_DIR = Path(__file__).resolve().parents[2]


def _resolve_source_path() -> Path:
    configured_path = Path(settings.RAG_SOURCE_PATH)
    candidate_paths: list[Path] = []

    if configured_path.is_absolute():
        candidate_paths.append(configured_path)

        # Common Docker-to-local fallback: /workspace/... -> <repo>/...
        try:
            relative_to_workspace = configured_path.relative_to(Path("/workspace"))
            candidate_paths.append(BASE_DIR / relative_to_workspace)
        except ValueError:
            pass
    else:
        candidate_paths.append(BASE_DIR / configured_path)

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    return candidate_paths[0]


def load_documents():
    source_path = _resolve_source_path()
    if not source_path.exists():
        raise FileNotFoundError(
            f"RAG source file not found at {source_path}. "
            "Update RAG_SOURCE_PATH in your environment configuration."
        )

    loader = TextLoader(str(source_path), encoding="utf-8")
    return loader.load()


docs = load_documents()
