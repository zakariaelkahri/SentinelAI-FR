from app.rag.retriever import retriever
from app.rag.llm import local_model
from app.rag.prompt import structured_prompt_template
from app.core.metrics import (
    rag_pipeline_calls_total,
    rag_latency_seconds,
    rag_retrieval_latency_seconds,
    rag_llm_latency_seconds,
    rag_errors_total,
    rag_retrieved_docs,
    rag_answer_length,
)
import time
import logging

logger = logging.getLogger(__name__)


# def _log_pipeline_to_mlflow(question, num_docs, retrieval_time, llm_time, total_time):
#     """Log pipeline metrics to MLflow, silently fail if unavailable."""
#     try:
#         import mlflow
#         mlflow.set_tracking_uri("http://mlflow:5000")
#         mlflow.set_experiment("RAG_Pipeline_Experiment")
#         with mlflow.start_run(run_name="RAG_Query"):
#             mlflow.log_param("question", question[:250])
#             mlflow.log_metric("num_retrieved_docs", num_docs)
#             mlflow.log_metric("retrieval_time_s", retrieval_time)
#             mlflow.log_metric("llm_inference_time_s", llm_time)
#             mlflow.log_metric("total_pipeline_time_s", total_time)
#     except Exception as e:
#         logger.warning(f"MLflow pipeline logging failed: {e}")


def answer_question(user_question: str) -> str:
    total_start = time.time()

    try:
        retrieval_start = time.time()
        docs = retriever.invoke(user_question)
        retrieval_time = time.time() - retrieval_start
        rag_retrieval_latency_seconds.observe(retrieval_time)

        rag_retrieved_docs.set(len(docs))

        context = "\n\n".join([doc.page_content for doc in docs])

        formatted_prompt = structured_prompt_template.format(
            context=context,
            question=user_question
        )

        llm_start = time.time()
        llm = local_model()
        response = llm.invoke(formatted_prompt)
        llm_time = time.time() - llm_start
        rag_llm_latency_seconds.observe(llm_time)

        total_time = time.time() - total_start
        rag_latency_seconds.observe(total_time)
        rag_pipeline_calls_total.inc()
        rag_answer_length.set(len(response.content))

        # _log_pipeline_to_mlflow(user_question, len(docs), retrieval_time, llm_time, total_time)

        return response.content

    except Exception as e:
        rag_pipeline_calls_total.inc()
        rag_errors_total.labels(error_type=type(e).__name__).inc()
        raise
