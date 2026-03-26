from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
import logging

logger = logging.getLogger(__name__)


# def _log_to_mlflow(structured_docs_count, final_chunks_count):
#     """Log metrics to MLflow, silently fail if unavailable."""
#     try:
#         import mlflow
#         mlflow.set_tracking_uri("http://mlflow:5000")
#         mlflow.set_experiment("Chunking_Experiment")
#         with mlflow.start_run(run_name="Hybrid_Chunking_Run"):
#             mlflow.log_metric("num_structured_docs", structured_docs_count)
#             mlflow.log_metric("num_final_chunks", final_chunks_count)
#             mlflow.log_param("chunk_size", 800)
#             mlflow.log_param("chunk_overlap", 150)
#     except Exception as e:
#         logger.warning(f"MLflow logging failed: {e}")


def hybrid_chunk(text):
    md_splitter = MarkdownHeaderTextSplitter([
        ("#", "Chapter"),
        ("##", "Section"),
        ("###", "Subsection"),
    ])

    structured_docs = md_splitter.split_text(text)

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    final_chunks = []

    for doc in structured_docs:
        sub_chunks = recursive_splitter.split_text(doc.page_content)

        for chunk in sub_chunks:
            final_chunks.append({
                "content": chunk,
                "metadata": doc.metadata
            })

    # _log_to_mlflow(len(structured_docs), len(final_chunks))

    return final_chunks
