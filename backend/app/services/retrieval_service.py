import asyncio
from typing import List, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    ScoredPoint,
    SearchRequest,
    NamedVector,
    NamedSparseVector,
    SparseVector,
)
from sentence_transformers import SentenceTransformer
from app.config import settings

_model: SentenceTransformer | None = None
_client: AsyncQdrantClient | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model


def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
    return _client


def _compute_bm25_sparse(text: str) -> SparseVector:
    """
    Lightweight BM25-inspired sparse vector using term frequency.
    Production use should replace this with a proper BM25 implementation or
    Qdrant's built-in sparse vector support with a trained BM25 encoder.
    """
    import re
    from collections import Counter
    import math

    tokens = re.findall(r"\w+", text.lower())
    tf = Counter(tokens)
    total = sum(tf.values())

    indices = []
    values = []
    for token, count in tf.items():
        # Simple hash-based index into a 30000-dim sparse space
        idx = hash(token) % 30000
        # Normalized TF score
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
    model = get_embedding_model()
    client = get_qdrant_client()

    loop = asyncio.get_event_loop()
    dense_vector = await loop.run_in_executor(
        None, lambda: model.encode(query).tolist()
    )

    try:
        if effective_mode == "hybrid":
            sparse_vector = _compute_bm25_sparse(query)

            # Qdrant hybrid search: prefetch dense + sparse, then RRF fusion
            from qdrant_client.http.models import Prefetch, FusionQuery, Fusion

            results: List[ScoredPoint] = await client.query_points(
                collection_name=settings.qdrant_collection,
                prefetch=[
                    Prefetch(
                        query=dense_vector,
                        using="dense",
                        limit=top_k * 2,
                    ),
                    Prefetch(
                        query=sparse_vector,
                        using="sparse",
                        limit=top_k * 2,
                    ),
                ],
                query=FusionQuery(fusion=Fusion.RRF),
                limit=top_k,
            )
        else:
            # Dense-only vector search
            results: List[ScoredPoint] = await client.query_points(
                collection_name=settings.qdrant_collection,
                query=dense_vector,
                using="dense",
                limit=top_k,
            )

        hits = []
        for point in results.points:
            payload = point.payload or {}
            hits.append(
                {
                    "id": payload.get("id", str(point.id)),
                    "question": payload.get("question", ""),
                    "answer": payload.get("answer", ""),
                    "score": float(point.score),
                }
            )

        return hits, effective_mode

    except Exception as e:
        # Fallback to dense-only if hybrid fails (e.g., sparse index not set up)
        results = await client.query_points(
            collection_name=settings.qdrant_collection,
            query=dense_vector,
            using="dense",
            limit=top_k,
        )
        hits = []
        for point in results.points:
            payload = point.payload or {}
            hits.append(
                {
                    "id": payload.get("id", str(point.id)),
                    "question": payload.get("question", ""),
                    "answer": payload.get("answer", ""),
                    "score": float(point.score),
                }
            )
        return hits, "dense_only"
