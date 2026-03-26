from app.core.config import settings
from app.rag.embeddings import documents, embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


def build_vectorstore(force_reindex: bool | None = None) -> QdrantVectorStore:
    should_reindex = settings.RAG_FORCE_REINDEX if force_reindex is None else force_reindex

    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    if should_reindex:
        try:
            client.delete_collection(collection_name=settings.QDRANT_COLLECTION)
            print(f"Deleted collection: {settings.QDRANT_COLLECTION}")
        except Exception as exc:
            print(f"Collection delete skipped: {exc}")

    vectorstore = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=settings.QDRANT_COLLECTION,
    )
    print(
        f"Indexed {len(documents)} chunks into collection '{settings.QDRANT_COLLECTION}'."
    )
    return vectorstore


if __name__ == "__main__":
    build_vectorstore()
