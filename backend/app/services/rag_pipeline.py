import time
from app.services.language_service import detect_language
from app.services.retrieval_service import retrieve
from app.services.confidence_service import compute_confidence, evaluate_handoff
from app.services.llm_service import generate_answer
from app.observability.langsmith_tracer import trace_rag_pipeline
from app.observability.prometheus_metrics import (
    query_latency_seconds,
    queries_total,
    handoff_triggered_total,
)
from app.models.schemas import ChatResponse


async def run_rag_pipeline(query: str, retrieval_mode: str | None = None) -> ChatResponse:
    start_time = time.perf_counter()

    language = detect_language(query)

    results, mode_used = await retrieve(query, mode=retrieval_mode)

    scores = [r["score"] for r in results]
    confidence = compute_confidence(scores)
    handoff_triggered, handoff_message = evaluate_handoff(confidence, language)

    sources = [r["id"] for r in results]

    if handoff_triggered:
        answer = handoff_message or ""
        estimated_cost = 0.0
    else:
        answer, estimated_cost = await generate_answer(query, results, language)

    trace_url = await trace_rag_pipeline(
        query=query,
        answer=answer,
        language=language,
        mode=mode_used,
        confidence=confidence,
        handoff=handoff_triggered,
        sources=sources,
        cost=estimated_cost,
    )

    elapsed = time.perf_counter() - start_time
    query_latency_seconds.observe(elapsed)
    queries_total.labels(language_detected=language).inc()
    if handoff_triggered:
        handoff_triggered_total.inc()

    return ChatResponse(
        answer=answer,
        language_detected=language,
        confidence=confidence,
        sources=sources,
        handoff_triggered=handoff_triggered,
        retrieval_mode_used=mode_used,
        estimated_cost_usd=estimated_cost,
        trace_url=trace_url,
    )
