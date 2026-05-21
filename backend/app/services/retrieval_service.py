import asyncio
import httpx
from typing import List, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    ScoredPoint,
    SparseVector,
)
from app.config import settings

_client: AsyncQdrantClient | None = None

HF_EMBED_URL = (
    "https://api-inference.huggingface.co/pipeline/feature-extraction/"
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


async def _get_dense_vector(text: str) -> list[float]:
    """Embed text via HF Inference API — no local model, no extra RAM."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            HF_EMBED_URL,
            json={"inputs": text, "options": {"wait_for_model": True}},
        )
        resp.raise_for_status()
        data = resp.json()

    # HF returns [float, ...] for sentence-transformers (already mean-pooled)
    if data and isinstance(data[0], float):
        return data
    # Fallback: [seq_len, dim] — mean-pool manually
    import numpy as np
    return list(np.mean(data, axis=0))


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        import os
        api_key = settings.qdrant_api_key or os.environ.get("QDRANT_API_KEY") or None
        _client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=api_key,
        )
    return _client


def _compute_bm25_sparse(text: str) -> SparseVector:
    import re
    from collections import Counter
    import math

    tokens = re.findall(r"\w+", text.lower())
    tf = Counter(tokens)
    total = sum(tf.values())

    indices, values = [], []
    for token, count in tf.items():
        idx = hash(token) % 30000
        score = count / total * math.log(1 + count)
        indices.append(abs(idx))
        values.append(float(score))

    return SparseVector(indices=indices, values=values)


async def retrieve(
    query: str,
    mode: str | None = None,
    top_k: int = 3,
) -> Tuple[List[dict], str]:
    """
    Returns (results, mode_used).
    Each result: {"id": str, "question": str, "answer": str, "score": float}
    """
    effective_mode = mode or settings.retrieval_mode
    client = get_qdrant_client()

    dense_vector = await _get_dense_vector(query)

    try:
        if effective_mode == "hybrid":
            sparse_vector = _compute_bm25_sparse(query)

            from qdrant_client.http.models import Prefetch, FusionQuery, Fusion

            results: List[ScoredPoint] = await client.query_points(
                collection_name=settings.qdrant_collection,
                prefetch=[
                    Prefetch(query=dense_vector, using="dense", limit=top_k * 2),
                    Prefetch(query=sparse_vector, using="sparse", limit=top_k * 2),
                ],
                query=FusionQuery(fusion=Fusion.RRF),
                limit=top_k,
            )
        else:
            results: List[ScoredPoint] = await client.query_points(
                collection_name=settings.qdrant_collection,
                query=dense_vector,
                using="dense",
                limit=top_k,
            )

        hits = []
        for point in results.points:
            payload = point.payload or {}
            hits.append({
                "id": payload.get("id", str(point.id)),
                "question": payload.get("question", ""),
                "answer": payload.get("answer", ""),
                "score": float(point.score),
            })

        return hits, effective_mode

    except Exception:
        try:
            results = await client.query_points(
                collection_name=settings.qdrant_collection,
                query=dense_vector,
                using="dense",
                limit=top_k,
            )
            hits = []
            for point in results.points:
                payload = point.payload or {}
                hits.append({
                    "id": payload.get("id", str(point.id)),
                    "question": payload.get("question", ""),
                    "answer": payload.get("answer", ""),
                    "score": float(point.score),
                })
            return hits, "dense_only"
        except Exception as e2:
            print(f"Retrieval completely failed: {e2}")
            return [], "unavailable"
