import re
import time

from app.core.config import settings
from app.core.metrics import (
    rag_answer_length,
    rag_errors_total,
    rag_latency_seconds,
    rag_llm_latency_seconds,
    rag_pipeline_calls_total,
    rag_pipeline_calls_by_status_total,
    rag_retrieval_latency_seconds,
    rag_retrieved_docs,
)
from app.rag.llm import local_model
from app.rag.prompt import structured_prompt_template
from app.rag.retriever import get_retriever
from app.rag.tracking import log_metrics, log_params, rag_mlflow_run


def _build_context(docs) -> str:
    selected_docs = docs[: settings.RAG_CONTEXT_DOCS]
    context = "\n\n".join(doc.page_content for doc in selected_docs)
    return context[: settings.RAG_MAX_CONTEXT_CHARS]


def _extract_text(response) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    return str(content).strip()


def _clean_text(text: str) -> str:
    cleaned = text.replace("\r", "")
    for token in ("**", "__", "`"):
        cleaned = cleaned.replace(token, "")
    cleaned = re.sub(r"^\s*#+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def answer_question(user_question: str) -> str:
    total_start = time.time()
    with rag_mlflow_run("rag_answer", tags={"entrypoint": "assistant"}) as mlflow:
        log_params(
            mlflow,
            {
                "question_chars": len(user_question),
                "retriever_k": settings.RAG_RETRIEVER_K,
                "reranker_model": settings.RAG_RERANKER_MODEL,
                "reranker_top_n": settings.RAG_RERANKER_TOP_N,
                "context_docs_limit": settings.RAG_CONTEXT_DOCS,
                "max_context_chars": settings.RAG_MAX_CONTEXT_CHARS,
                "llm_model": settings.OLLAMA_MODEL,
                "embedding_model": settings.EMBEDDING_MODEL,
            },
        )

        try:
            retrieval_start = time.time()
            docs = get_retriever().invoke(user_question)
            retrieval_latency = time.time() - retrieval_start
            rag_retrieval_latency_seconds.observe(retrieval_latency)

            retrieved_docs_count = len(docs)
            rag_retrieved_docs.set(retrieved_docs_count)
            context = _build_context(docs)
            context_chars = len(context)

            prompt = structured_prompt_template.format(
                context=context,
                question=user_question,
            )

            llm_start = time.time()
            response = local_model().invoke(prompt)
            llm_latency = time.time() - llm_start
            rag_llm_latency_seconds.observe(llm_latency)

            answer = _clean_text(_extract_text(response))
            answer_chars = len(answer)

            total_latency = time.time() - total_start
            rag_latency_seconds.observe(total_latency)
            rag_pipeline_calls_total.inc()
            rag_pipeline_calls_by_status_total.labels(status="success").inc()
            rag_answer_length.set(answer_chars)

            log_metrics(
                mlflow,
                {
                    "retrieved_docs_count": float(retrieved_docs_count),
                    "context_chars": float(context_chars),
                    "answer_chars": float(answer_chars),
                    "retrieval_latency_seconds": retrieval_latency,
                    "llm_latency_seconds": llm_latency,
                    "total_latency_seconds": total_latency,
                    "pipeline_success": 1.0,
                },
            )
            return answer

        except Exception as exc:
            total_latency = time.time() - total_start
            rag_latency_seconds.observe(total_latency)
            rag_pipeline_calls_total.inc()
            rag_pipeline_calls_by_status_total.labels(status="error").inc()
            rag_errors_total.labels(error_type=type(exc).__name__).inc()

            if mlflow is not None:
                try:
                    mlflow.set_tag("error_type", type(exc).__name__)
                except Exception:
                    pass

            log_metrics(
                mlflow,
                {
                    "total_latency_seconds": total_latency,
                    "pipeline_success": 0.0,
                },
            )
            raise


# if __name__ == "__main__":
#     print(answer_question("What are the duties of a security officer?"))
