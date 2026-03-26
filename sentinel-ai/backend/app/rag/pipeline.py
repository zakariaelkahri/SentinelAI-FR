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

        return response.content

    except Exception as e:
        rag_pipeline_calls_total.inc()
        rag_errors_total.labels(error_type=type(e).__name__).inc()
        raise

answer_question("What are the duties of a security officer?")
