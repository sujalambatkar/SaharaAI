from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.models.query_log import QueryLog, RetrievalModeSetting
from app.services.rag_pipeline import run_rag_pipeline
from sqlalchemy import select

router = APIRouter()


async def _get_active_retrieval_mode(db: AsyncSession) -> str | None:
    result = await db.execute(
        select(RetrievalModeSetting).order_by(RetrievalModeSetting.updated_at.desc()).limit(1)
    )
    setting = result.scalar_one_or_none()
    return setting.mode if setting else None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Per-request override > DB setting > env var (handled inside pipeline)
    mode_override = request.retrieval_mode or await _get_active_retrieval_mode(db)

    response = await run_rag_pipeline(request.query, retrieval_mode=mode_override)

    log = QueryLog(
        query=request.query,
        answer=response.answer,
        language_detected=response.language_detected,
        confidence=response.confidence,
        handoff_triggered=response.handoff_triggered,
        retrieval_mode_used=response.retrieval_mode_used,
        estimated_cost_usd=response.estimated_cost_usd,
        trace_url=response.trace_url,
        sources=",".join(response.sources),
    )
    db.add(log)

    return response
