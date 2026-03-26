from prometheus_client import Counter, Gauge, Histogram


rag_pipeline_calls_total = Counter(
    "rag_pipeline_calls_total",
    "Total number of RAG pipeline calls",
)

rag_latency_seconds = Histogram(
    "rag_latency_seconds",
    "Total RAG pipeline latency in seconds",
)

rag_retrieval_latency_seconds = Histogram(
    "rag_retrieval_latency_seconds",
    "RAG document retrieval latency in seconds",
)

rag_llm_latency_seconds = Histogram(
    "rag_llm_latency_seconds",
    "RAG LLM generation latency in seconds",
)

rag_errors_total = Counter(
    "rag_errors_total",
    "Total number of RAG pipeline errors",
    ["error_type"],
)

rag_retrieved_docs = Gauge(
    "rag_retrieved_docs",
    "Number of documents returned by retriever",
)

rag_answer_length = Gauge(
    "rag_answer_length",
    "Length of generated RAG answer in characters",
)

