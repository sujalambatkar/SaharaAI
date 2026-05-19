from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import chat, dashboard, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
