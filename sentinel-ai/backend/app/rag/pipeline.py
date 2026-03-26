import re
import time

from app.core.config import settings
from app.core.metrics import (
    rag_answer_length,
    rag_errors_total,
    rag_latency_seconds,
    rag_llm_latency_seconds,
    rag_pipeline_calls_total,
    rag_retrieval_latency_seconds,
    rag_retrieved_docs,
)
from app.rag.llm import local_model
from app.rag.prompt import structured_prompt_template
from app.rag.retriever import get_retriever


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

    try:
        retrieval_start = time.time()
        docs = get_retriever().invoke(user_question)
        rag_retrieval_latency_seconds.observe(time.time() - retrieval_start)

        rag_retrieved_docs.set(len(docs))
        context = _build_context(docs)

        prompt = structured_prompt_template.format(
            context=context,
            question=user_question,
        )

        llm_start = time.time()
        response = local_model().invoke(prompt)
        rag_llm_latency_seconds.observe(time.time() - llm_start)

        answer = _clean_text(_extract_text(response))

        rag_latency_seconds.observe(time.time() - total_start)
        rag_pipeline_calls_total.inc()
        rag_answer_length.set(len(answer))
        return answer

    except Exception as exc:
        rag_pipeline_calls_total.inc()
        rag_errors_total.labels(error_type=type(exc).__name__).inc()
        raise


if __name__ == "__main__":
    print(answer_question("What are the duties of a security officer?"))
