import os
from typing import Optional
from app.config import settings


async def trace_rag_pipeline(
    query: str,
    answer: str,
    language: str,
    mode: str,
    confidence: float,
    handoff: bool,
    sources: list[str],
    cost: float,
) -> Optional[str]:
    """
    Wraps the RAG pipeline result in a LangSmith trace.
    Returns the trace URL if LangSmith is configured, otherwise None.
    """
    if not settings.langsmith_api_key:
        return None

    try:
        from langsmith import Client
        from langsmith.run_helpers import traceable

        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")

        client = Client(api_key=settings.langsmith_api_key)

        run = client.create_run(
            name="sahara-rag-pipeline",
            run_type="chain",
            inputs={"query": query},
            outputs={"answer": answer},
            extra={
                "metadata": {
                    "language_detected": language,
                    "retrieval_mode_used": mode,
                    "confidence": confidence,
                    "handoff_triggered": handoff,
                    "sources": sources,
                    "estimated_cost_usd": cost,
                }
            },
            project_name=settings.langsmith_project,
        )
        client.update_run(run_id=run.id, end_time=None)

        run_id = str(run.id)
        trace_url = f"https://smith.langchain.com/public/{run_id}/r"
        return trace_url

    except Exception:
        # LangSmith tracing is non-critical — never fail the pipeline
        return None
