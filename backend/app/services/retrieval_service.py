import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from app.config import settings

_kb_entries: list[dict] | None = None
_qdrant_client = None

KB_PATH = Path("/data/kb.jsonl")


def _load_kb() -> list[dict]:
    global _kb_entries
    if _kb_entries is None:
        if KB_PATH.exists():
            _kb_entries = []
            with KB_PATH.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        _kb_entries.append(json.loads(line))
        else:
            _kb_entries = []
    return _kb_entries


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _bm25_score(query_tokens: list[str], doc_tokens: list[str], avg_dl: float,
                k1: float = 1.5, b: float = 0.75) -> float:
    dl = len(doc_tokens)
    tf = Counter(doc_tokens)
    N = max(len(_load_kb()), 1)
    score = 0.0
    for token in set(query_tokens):
        freq = tf.get(token, 0)
        if freq == 0:
            continue
        idf = math.log((N - freq + 0.5) / (freq + 0.5) + 1)
        score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * dl / avg_dl))
    return score


def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        import os
        from qdrant_client import AsyncQdrantClient
        api_key = settings.qdrant_api_key or os.environ.get("QDRANT_API_KEY") or None
        _qdrant_client = AsyncQdrantClient(url=settings.qdrant_url, api_key=api_key)
    return _qdrant_client


async def retrieve(
    query: str,
    mode: str | None = None,
    top_k: int = 3,
) -> Tuple[List[dict], str]:
    """
    Returns (results, mode_used).
    Each result: {"id": str, "question": str, "answer": str, "score": float}
    """
    entries = _load_kb()

    if not entries:
        return [], "unavailable"

    query_tokens = _tokenize(query)
    if not query_tokens:
        return [], "bm25"

    doc_token_lists = [_tokenize(e["question"] + " " + e["answer"]) for e in entries]
    avg_dl = sum(len(t) for t in doc_token_lists) / len(doc_token_lists)

    scored = []
    for entry, doc_tokens in zip(entries, doc_token_lists):
        score = _bm25_score(query_tokens, doc_tokens, avg_dl)
        scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    hits = [
        {
            "id": e["id"],
            "question": e["question"],
            "answer": e["answer"],
            "score": round(s, 4),
        }
        for s, e in scored[:top_k]
        if s > 0
    ]

    return hits, "bm25"
