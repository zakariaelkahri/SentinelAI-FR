from pathlib import Path

from langchain_community.document_loaders import TextLoader

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]


def _candidate_source_paths() -> list[Path]:
    configured = Path(settings.RAG_SOURCE_PATH)
    if not configured.is_absolute():
        return [BASE_DIR / configured]

    candidates = [configured]
    if str(configured).startswith("/workspace/"):
        candidates.append(BASE_DIR / configured.relative_to("/workspace"))
    return candidates


def load_documents():
    source_path = next((path for path in _candidate_source_paths() if path.exists()), None)
    if source_path is None:
        tried = ", ".join(str(path) for path in _candidate_source_paths())
        raise FileNotFoundError(
            f"RAG source file not found. Paths checked: {tried}. "
            "Update RAG_SOURCE_PATH in your environment configuration."
        )

    return TextLoader(str(source_path), encoding="utf-8").load()


docs = load_documents()
