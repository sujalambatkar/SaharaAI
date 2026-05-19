from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User's query")
    retrieval_mode: Optional[str] = None  # override env var per-request if provided


class ChatResponse(BaseModel):
    answer: str
    language_detected: Literal["EN", "HI", "HINGLISH"]
    confidence: float
    sources: List[str]
    handoff_triggered: bool
    retrieval_mode_used: str
    estimated_cost_usd: float
    trace_url: Optional[str] = None


class DashboardStats(BaseModel):
    total_queries_today: int
    avg_confidence: float
    handoff_rate_pct: float
    most_common_language: str
    estimated_cost_today_usd: float
    queries_by_language: dict
    recent_queries: List[dict]


class DailyMetric(BaseModel):
    date: str
    cost_usd: float
    query_count: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    daily_metrics: List[DailyMetric]
    current_retrieval_mode: str


class RetrievalModeUpdate(BaseModel):
    mode: Literal["dense_only", "hybrid"]
