from pathlib import Path
from langchain_community.document_loaders import TextLoader

# Resolve project root inside the container: /workspace
BASE_DIR = Path(__file__).resolve().parents[2]
MANUAL_PATH = BASE_DIR / "data" / "processing" / "Guide-des-Protocoles.md"

if not MANUAL_PATH.exists():
    raise FileNotFoundError(
        f"Manual file not found at {MANUAL_PATH}. "
        "Make sure data/processed/manual.md exists in the project root."
    )

loader = TextLoader(str(MANUAL_PATH), encoding="utf-8")
docs = loader.load()
