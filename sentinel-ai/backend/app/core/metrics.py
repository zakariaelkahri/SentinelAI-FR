from prometheus_client import Counter, Gauge, Histogram


http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests processed",
    ["method", "route", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "route", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes (from Content-Length header)",
    ["method", "route"],
    buckets=(100, 500, 1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000),
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes (from Content-Length header)",
    ["method", "route", "status_code"],
    buckets=(100, 500, 1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000),
)

http_request_exceptions_total = Counter(
    "http_request_exceptions_total",
    "Total number of unhandled HTTP request exceptions",
    ["method", "route", "exception_type"],
)


rag_pipeline_calls_total = Counter(
    "rag_pipeline_calls_total",
    "Total number of RAG pipeline calls",
)

rag_pipeline_calls_by_status_total = Counter(
    "rag_pipeline_calls_by_status_total",
    "Total number of RAG pipeline calls grouped by status",
    ["status"],
)

rag_latency_seconds = Histogram(
    "rag_latency_seconds",
    "Total RAG pipeline latency in seconds",
    buckets=(0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89),
)

rag_retrieval_latency_seconds = Histogram(
    "rag_retrieval_latency_seconds",
    "RAG document retrieval latency in seconds",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13),
)

rag_llm_latency_seconds = Histogram(
    "rag_llm_latency_seconds",
    "RAG LLM generation latency in seconds",
    buckets=(0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55),
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
