from app.rag.chunking import hybrid_chunk
from app.rag.loader import docs
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

md_text = docs[0].page_content
chunks = hybrid_chunk(md_text)

documents = [
    Document(page_content=chunk["content"], metadata=chunk.get("metadata", {}))
    for chunk in chunks
]

embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)


# def _log_embeddings_to_mlflow():
#     """Log embedding params to MLflow, silently fail if unavailable."""
#     try:
#         import mlflow
#         mlflow.set_tracking_uri("http://mlflow:5000")
#         mlflow.set_experiment("Embedding_Experiment")
#         with mlflow.start_run(run_name="Embedding_Config"):
#             mlflow.log_param("embedding_model", settings.EMBEDDING_MODEL)
#             mlflow.log_metric("num_documents", len(documents))
#             mlflow.log_metric("num_chunks", len(chunks))
#     except Exception as e:
#         logger.warning(f"MLflow embedding logging failed: {e}")


# _log_embeddings_to_mlflow()
