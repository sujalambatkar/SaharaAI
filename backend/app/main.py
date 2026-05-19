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
    await init_db()
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
    return {"status": "ok", "service": "SaharaAI"}
