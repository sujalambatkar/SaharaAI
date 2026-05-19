from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    language_detected = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    handoff_triggered = Column(Boolean, default=False, nullable=False)
    retrieval_mode_used = Column(String(20), nullable=False)
    estimated_cost_usd = Column(Float, nullable=False)
    trace_url = Column(String(500), nullable=True)
    sources = Column(Text, nullable=True)  # comma-separated source IDs
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RetrievalModeSetting(Base):
    __tablename__ = "retrieval_mode_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mode = Column(String(20), nullable=False, default="hybrid")
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
