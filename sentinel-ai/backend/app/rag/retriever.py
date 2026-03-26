from app.rag.embeddings import embeddings
from app.core.config import settings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import logging

logger = logging.getLogger(__name__)

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=settings.QDRANT_COLLECTION,
    embedding=embeddings
)

BASE_RETRIEVER_K = 20
RERANKER_MODEL = "BAAI/bge-reranker-base"
RERANKER_TOP_N = 5

base_retriever = vectorstore.as_retriever(search_kwargs={"k": BASE_RETRIEVER_K})

model = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL)

compressor = CrossEncoderReranker(model=model, top_n=RERANKER_TOP_N)

retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)


def get_retriever():
    return retriever


# def _log_retriever_to_mlflow():
#     """Log retriever params to MLflow, silently fail if unavailable."""
#     try:
#         import mlflow
#         mlflow.set_tracking_uri("http://mlflow:5000")
#         mlflow.set_experiment("Retriever_Experiment")
#         with mlflow.start_run(run_name="Retriever_Config"):
#             mlflow.log_param("base_retriever_k", BASE_RETRIEVER_K)
#             mlflow.log_param("reranker_model", RERANKER_MODEL)
#             mlflow.log_param("reranker_top_n", RERANKER_TOP_N)
#             mlflow.log_param("vectorstore_collection", settings.QDRANT_COLLECTION)
#             mlflow.log_param("retriever_type", "ContextualCompressionRetriever")
#     except Exception as e:
#         logger.warning(f"MLflow retriever logging failed: {e}")


# _log_retriever_to_mlflow()
