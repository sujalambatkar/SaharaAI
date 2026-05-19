"""
5 pytest tests for SaharaAI pipeline.
Run: pytest tests/test_pipeline.py -v
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# ---------------------------------------------------------------------------
# Test 1: Language detection — Hindi query
# ---------------------------------------------------------------------------
def test_language_detection_hindi():
    from app.services.language_service import detect_language

    result = detect_language("मेरा ऑर्डर कहाँ है")
    assert result == "HI", f"Expected HI, got {result}"


# ---------------------------------------------------------------------------
# Test 2: Language detection — Hinglish query
# ---------------------------------------------------------------------------
def test_language_detection_hinglish():
    from app.services.language_service import detect_language

    result = detect_language("Mera order kab aayega?")
    assert result == "HINGLISH", f"Expected HINGLISH, got {result}"


# ---------------------------------------------------------------------------
# Test 3: Retrieval returns results (mocked Qdrant)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_retrieval_returns_results():
    from app.services import retrieval_service

    mock_point = MagicMock()
    mock_point.id = "some-uuid"
    mock_point.score = 0.85
    mock_point.payload = {
        "id": "kb_001",
        "question": "How do I track my order?",
        "answer": "Visit Track Order section.",
    }

    mock_result = MagicMock()
    mock_result.points = [mock_point]

    mock_client = AsyncMock()
    mock_client.query_points.return_value = mock_result

    with patch.object(retrieval_service, "get_qdrant_client", return_value=mock_client):
        results, mode = await retrieval_service.retrieve("Where is my order?", mode="dense_only")

    assert len(results) >= 1, "Expected at least 1 retrieval result"
    assert results[0]["id"] == "kb_001"
    assert results[0]["score"] == pytest.approx(0.85)


# ---------------------------------------------------------------------------
# Test 4: Low confidence score triggers handoff
# ---------------------------------------------------------------------------
def test_confidence_below_threshold_triggers_handoff():
    from app.services.confidence_service import compute_confidence, evaluate_handoff

    # Scores that normalize to ~0.3 confidence (well below 0.65 threshold)
    raw_scores = [-0.4, -0.5, -0.3]  # cosine scores in [-1, 1]
    confidence = compute_confidence(raw_scores)

    assert confidence < 0.65, f"Expected confidence < 0.65, got {confidence}"

    handoff_triggered, message = evaluate_handoff(confidence, "EN")
    assert handoff_triggered is True
    assert message is not None
    assert "support" in message.lower()


# ---------------------------------------------------------------------------
# Test 5: Prometheus /metrics endpoint returns 200
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint():
    from app.main import app

    # Patch DB init so we don't need a real Postgres in tests
    with patch("app.database.init_db", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics")

    assert response.status_code == 200
    assert "queries_total" in response.text or "query_latency" in response.text
