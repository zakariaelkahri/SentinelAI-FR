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
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embeddings,
    )

    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": settings.RAG_RETRIEVER_K}
    )
    reranker = CrossEncoderReranker(
        model=HuggingFaceCrossEncoder(model_name=settings.RAG_RERANKER_MODEL),
        top_n=settings.RAG_RERANKER_TOP_N,
    )

    return ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever,
    )
