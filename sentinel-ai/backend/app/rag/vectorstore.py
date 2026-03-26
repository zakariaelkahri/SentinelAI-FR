from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import settings
from app.rag.embeddings import documents, embeddings


def build_vectorstore(force_reindex: bool | None = None) -> QdrantVectorStore:
    should_reindex = settings.RAG_FORCE_REINDEX if force_reindex is None else force_reindex
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    if should_reindex:
        try:
            client.delete_collection(collection_name=settings.QDRANT_COLLECTION)
        except Exception:
            pass

    return QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=settings.QDRANT_COLLECTION,
    )


if __name__ == "__main__":
    build_vectorstore()
