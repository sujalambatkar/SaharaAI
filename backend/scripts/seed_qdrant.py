"""
Seed script: reads /data/kb.jsonl, embeds each entry with
paraphrase-multilingual-MiniLM-L12-v2, and upserts into Qdrant.

Run manually: python scripts/seed_qdrant.py
Runs automatically on container startup via Dockerfile CMD.
"""

import json
import os
import sys
import time
import uuid
import re
from pathlib import Path
from collections import Counter

# Allow running from /backend root
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    PointStruct,
    SparseVector,
    models,
)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
COLLECTION = os.getenv("QDRANT_COLLECTION", "sahara_kb")
KB_PATH = Path(os.getenv("KB_PATH", "/data/kb.jsonl"))
DENSE_DIM = 384  # paraphrase-multilingual-MiniLM-L12-v2 output size
SPARSE_DIM = 30000


def compute_sparse_vector(text: str) -> SparseVector:
    """BM25-inspired sparse vector from term frequencies."""
    import math

    tokens = re.findall(r"\w+", text.lower())
    tf = Counter(tokens)
    total = sum(tf.values())
    indices, values = [], []
    seen = set()
    for token, count in tf.items():
        idx = abs(hash(token) % SPARSE_DIM)
        if idx in seen:
            continue
        seen.add(idx)
        score = count / total * math.log(1 + count)
        indices.append(idx)
        values.append(float(score))
    return SparseVector(indices=indices, values=values)


def wait_for_qdrant(client: QdrantClient, retries: int = 5, delay: int = 3) -> None:
    for attempt in range(retries):
        try:
            client.get_collections()
            print("Qdrant is ready.")
            return
        except Exception as e:
            print(f"Waiting for Qdrant... ({attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Qdrant did not become ready in time.")


def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config={"dense": VectorParams(size=DENSE_DIM, distance=Distance.COSINE)},
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))
            },
        )
        print(f"Created collection: {COLLECTION}")
    else:
        print(f"Collection '{COLLECTION}' already exists — upserting.")


def load_kb(path: Path) -> list[dict]:
    entries = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    print(f"Loaded {len(entries)} KB entries from {path}")
    return entries


def seed(entries: list[dict], model, client: QdrantClient) -> None:
    texts = [e["question"] + " " + e["answer"] for e in entries]
    print("Embedding entries...")
    dense_vectors = list(model.embed(texts))

    points = []
    for entry, dense_vec in zip(entries, dense_vectors):
        sparse_vec = compute_sparse_vector(entry["question"] + " " + entry["answer"])
        point = PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, entry["id"])),
            vector={
                "dense": dense_vec.tolist(),
                "sparse": sparse_vec,
            },
            payload={
                "id": entry["id"],
                "question": entry["question"],
                "answer": entry["answer"],
                "lang": entry["lang"],
                "topic": entry.get("topic", "general"),
            },
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Upserted {len(points)} points into '{COLLECTION}'.")


def main() -> None:
    print("=== SaharaAI Qdrant Seed Script ===")
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=5)
        wait_for_qdrant(client)
        ensure_collection(client)

        if not KB_PATH.exists():
            print(f"WARNING: KB file not found at {KB_PATH} — skipping seed. API will start without KB data.")
            return

        entries = load_kb(KB_PATH)
        model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        seed(entries, model, client)
        print("Seeding complete.")
    except Exception as e:
        print(f"WARNING: Seeding failed ({e}) — continuing to start API server anyway.")


if __name__ == "__main__":
    main()
