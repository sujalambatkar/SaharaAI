from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.query_log import QueryLog, RetrievalModeSetting
from app.models.schemas import DashboardResponse, DashboardStats, DailyMetric, RetrievalModeUpdate
from app.config import settings

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Today's queries
    today_result = await db.execute(
        select(QueryLog).where(QueryLog.created_at >= today_start)
    )
    today_logs = today_result.scalars().all()

    total_today = len(today_logs)
    avg_confidence = (
        sum(l.confidence for l in today_logs) / total_today if total_today else 0.0
    )
    handoff_count = sum(1 for l in today_logs if l.handoff_triggered)
    handoff_rate = (handoff_count / total_today * 100) if total_today else 0.0
    total_cost_today = sum(l.estimated_cost_usd for l in today_logs)

    lang_counts: dict[str, int] = {}
    for log in today_logs:
        lang_counts[log.language_detected] = lang_counts.get(log.language_detected, 0) + 1
    most_common_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "EN"

    recent_queries = [
        {
            "query": l.query[:80],
            "language": l.language_detected,
            "confidence": round(l.confidence, 3),
            "handoff": l.handoff_triggered,
            "created_at": l.created_at.isoformat() if l.created_at else "",
        }
        for l in sorted(today_logs, key=lambda x: x.created_at or datetime.min, reverse=True)[:10]
    ]

    # Daily metrics for the past 7 days
    seven_days_ago = today_start - timedelta(days=6)
    daily_result = await db.execute(
        select(
            cast(QueryLog.created_at, Date).label("date"),
            func.sum(QueryLog.estimated_cost_usd).label("cost"),
            func.count(QueryLog.id).label("count"),
        )
        .where(QueryLog.created_at >= seven_days_ago)
        .group_by(cast(QueryLog.created_at, Date))
        .order_by(cast(QueryLog.created_at, Date))
    )
    daily_rows = daily_result.all()
    daily_metrics = [
        DailyMetric(date=str(row.date), cost_usd=round(row.cost or 0.0, 6), query_count=row.count)
        for row in daily_rows
    ]

    # Active retrieval mode from DB (fall back to env)
    mode_result = await db.execute(
        select(RetrievalModeSetting).order_by(RetrievalModeSetting.updated_at.desc()).limit(1)
    )
    mode_setting = mode_result.scalar_one_or_none()
    current_mode = mode_setting.mode if mode_setting else settings.retrieval_mode

    return DashboardResponse(
        stats=DashboardStats(
            total_queries_today=total_today,
            avg_confidence=round(avg_confidence, 3),
            handoff_rate_pct=round(handoff_rate, 1),
            most_common_language=most_common_lang,
            estimated_cost_today_usd=round(total_cost_today, 6),
            queries_by_language=lang_counts,
            recent_queries=recent_queries,
        ),
        daily_metrics=daily_metrics,
        current_retrieval_mode=current_mode,
    )


@router.patch("/dashboard/retrieval-mode", response_model=dict)
async def update_retrieval_mode(
    body: RetrievalModeUpdate, db: AsyncSession = Depends(get_db)
):
    new_setting = RetrievalModeSetting(mode=body.mode)
    db.add(new_setting)
    return {"status": "ok", "retrieval_mode": body.mode}
