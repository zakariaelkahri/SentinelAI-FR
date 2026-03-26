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


ARABIC_CHAR_PATTERN = re.compile(r"[\u0600-\u06FF]")
FRENCH_ACCENT_PATTERN = re.compile(r"[àâçéèêëîïôûùüÿœæ]")
FRENCH_MARKERS = {
    "bonjour",
    "salut",
    "merci",
    "quel",
    "quelle",
    "quels",
    "quelles",
    "comment",
    "pourquoi",
    "est",
    "sont",
    "les",
    "des",
    "une",
    "un",
    "de",
    "la",
    "le",
    "du",
    "au",
    "aux",
    "pour",
    "avec",
    "sans",
    "que",
    "qui",
    "quoi",
    "ou",
    "ou",
}


def _detect_response_language(question: str) -> str:
    if ARABIC_CHAR_PATTERN.search(question):
        return "Arabic"

    lowered = question.lower()
    if FRENCH_ACCENT_PATTERN.search(lowered):
        return "French"

    words = re.findall(r"[a-zA-ZÀ-ÿ']+", lowered)
    french_marker_hits = sum(1 for word in words if word in FRENCH_MARKERS)
    if french_marker_hits >= 2:
        return "French"

    return "English"


def _build_context(docs) -> str:
    selected_docs = docs[: settings.RAG_CONTEXT_DOCS]
    context = "\n\n".join(doc.page_content for doc in selected_docs)
    return context[: settings.RAG_MAX_CONTEXT_CHARS]


def _response_to_text(response) -> str:
    if isinstance(response, str):
        return response.strip()

    content = getattr(response, "content", "")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()

    return str(content).strip()


def _clean_answer_text(answer: str) -> str:
    cleaned = answer.replace("\r", "")
    cleaned = cleaned.replace("**", "").replace("__", "").replace("`", "")
    cleaned = re.sub(r"^\s*#+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def answer_question(user_question: str) -> str:
    total_start = time.time()
    response_language = _detect_response_language(user_question)

    try:
        retrieval_start = time.time()
        docs = get_retriever().invoke(user_question)
        retrieval_time = time.time() - retrieval_start
        rag_retrieval_latency_seconds.observe(retrieval_time)

        rag_retrieved_docs.set(len(docs))
        context = _build_context(docs)

        formatted_prompt = structured_prompt_template.format(
            context=context,
            question=user_question,
            response_language=response_language,
        )

        llm_start = time.time()
        llm = local_model()
        response = llm.invoke(formatted_prompt)
        llm_time = time.time() - llm_start
        rag_llm_latency_seconds.observe(llm_time)

        answer = _clean_answer_text(_response_to_text(response))

        total_time = time.time() - total_start
        rag_latency_seconds.observe(total_time)
        rag_pipeline_calls_total.inc()
        rag_answer_length.set(len(answer))

        return answer

    except Exception as exc:
        rag_pipeline_calls_total.inc()
        rag_errors_total.labels(error_type=type(exc).__name__).inc()
        raise


if __name__ == "__main__":
    print(answer_question("What are the duties of a security officer?"))
