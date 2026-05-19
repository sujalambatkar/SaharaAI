from prometheus_client import Histogram, Counter, REGISTRY

query_latency_seconds = Histogram(
    "query_latency_seconds",
    "End-to-end RAG pipeline latency in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],
)

queries_total = Counter(
    "queries_total",
    "Total number of queries processed, labelled by detected language",
    labelnames=["language_detected"],
)

handoff_triggered_total = Counter(
    "handoff_triggered_total",
    "Total number of queries that triggered a human handoff",
)
