from functools import lru_cache

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import settings
from app.rag.embeddings import embeddings


@lru_cache(maxsize=1)
def get_retriever() -> ContextualCompressionRetriever:
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    try:
        collection_exists = client.collection_exists(settings.QDRANT_COLLECTION)
    except Exception as exc:
        raise RuntimeError(
            f"Unable to connect to Qdrant at {settings.QDRANT_URL}. "
            f"Original error: {exc}"
        ) from exc

    if not collection_exists:
        raise RuntimeError(
            f"Qdrant collection '{settings.QDRANT_COLLECTION}' does not exist. "
            "Build the index first by running: python -m app.rag.vectorstore"
        )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embeddings,
    )

    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": settings.RAG_RETRIEVER_K}
    )

    reranker_model = HuggingFaceCrossEncoder(model_name=settings.RAG_RERANKER_MODEL)
    compressor = CrossEncoderReranker(
        model=reranker_model,
        top_n=settings.RAG_RERANKER_TOP_N,
    )

    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )

