import asyncio
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import chat, dashboard, metrics


async def _seed_qdrant_background() -> None:
    try:
        from app.services.retrieval_service import get_qdrant_client
        client = get_qdrant_client()
        info = await client.get_collection(settings.qdrant_collection)
        if info.points_count and info.points_count > 0:
            print(f"Qdrant already has {info.points_count} points — skipping seed.")
            return
    except Exception:
        pass
    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "scripts/seed_qdrant.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        print(stdout.decode())
    except Exception as e:
        print(f"Background Qdrant seed failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        print(f"WARNING: DB init failed ({e}) — continuing startup, retries will happen on first request")
    asyncio.create_task(_seed_qdrant_background())
    yield


app = FastAPI(
    title="SaharaAI Customer Support API",
    description="Multilingual RAG-based customer support agent for Sahara D2C brand",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, tags=["chat"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(metrics.router, tags=["observability"])


@app.get("/health")
async def health():
    from app.services.retrieval_service import get_qdrant_client
    from app.config import settings
    try:
        client = get_qdrant_client()
        cols = await client.get_collections()
        names = [c.name for c in cols.collections]
        qdrant_status = f"ok ({names})"
    except Exception as e:
        qdrant_status = f"error: {e}"
    import os
    env_key = os.environ.get("QDRANT_API_KEY", "")
    return {"status": "ok", "service": "SaharaAI", "qdrant": qdrant_status, "qdrant_url_prefix": settings.qdrant_url[:40], "qdrant_key_pydantic": bool(settings.qdrant_api_key), "qdrant_key_env": bool(env_key), "qdrant_key_preview": env_key[:6] if env_key else "empty"}
