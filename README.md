<div align="center">

# 🌵 SaharaAI

### Multilingual Customer Support Agent for Indian D2C Brands

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=next.js&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=flat)
![Llama](https://img.shields.io/badge/Llama_3.3_70B-via_Groq-F54E00?style=flat)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**Answers customer queries in Hindi, English, and Hinglish — with full RAG pipeline, hybrid vector search, confidence scoring, and real-time observability.**

[Live Demo](#) · [Architecture](#llmops-architecture) · [Quick Start](#quick-start) · [Deploy](#deployment)

</div>

---

## What is SaharaAI?

SaharaAI is a production-ready RAG (Retrieval-Augmented Generation) customer support agent built for **Sahara**, a fictional Indian D2C e-commerce brand. It automatically detects whether the customer is writing in Hindi, English, or Hinglish — then retrieves relevant answers from a structured knowledge base and generates a contextual, on-brand response.

When the system isn't confident enough in its answer, it gracefully escalates to a human agent instead of hallucinating.

**Supported topics:** Order tracking · Returns & exchanges · Payment/UPI issues · Delivery zones · Product care · Account issues

---

## Features

- **Automatic language detection** — classifies each query as EN / HI / HINGLISH and responds in kind
- **Hybrid vector search** — dense (semantic) + BM25 sparse retrieval fused via Reciprocal Rank Fusion in Qdrant
- **Confidence scoring** — normalized average of top-3 retrieval scores; triggers human handoff below 65%
- **Groq + Llama 3.3 70B** — fast inference (~500 tok/s), 14,400 free requests/day
- **LangSmith tracing** — every query produces a full trace URL in the API response
- **Prometheus metrics** — latency histogram, query counter (by language), handoff counter
- **PostgreSQL logging** — cost + confidence logged per query; dashboard auto-refreshes every 30s
- **RAGAS evaluation** — offline eval script comparing dense-only vs hybrid across 20 test queries
- **One-command startup** — `docker compose up --build`

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI 0.115, Python 3.11, async SQLAlchemy + asyncpg |
| **Frontend** | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| **Vector DB** | Qdrant — hybrid search (dense + BM25 sparse, RRF fusion) |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` (handles Hindi natively) |
| **LLM** | Llama 3.3 70B via Groq API |
| **Database** | PostgreSQL 16 (cost + confidence logs) |
| **Observability** | LangSmith (tracing) + Prometheus (metrics) |
| **Infra** | Docker Compose (5 services) |

---

## Why Qdrant over Weaviate / Pinecone?

| Criterion | **Qdrant** ✓ | Weaviate | Pinecone |
|---|---|---|---|
| Hybrid search | Native dense + sparse, RRF — zero config | GraphQL module, complex setup | Separate sparse index, extra cost |
| Self-hosting | Single Docker image, ~150 MB | Heavy JVM + Go layer | Managed-only |
| Async Python client | `AsyncQdrantClient` — first-class | Mature but more complex | Sync-first |
| Sparse vector support | `SparseVectorParams` built-in | BM25 via module only | Manual encoding required |
| Free self-hosted tier | Forever free OSS | OSS but resource-heavy | Not available |

---

## How Confidence Scoring Works

```
confidence = mean([ (score + 1) / 2  for score in top_3_retrieval_scores ])
```

Qdrant cosine scores are in `[-1, 1]`. We shift them to `[0, 1]` for readability.

**Threshold: 0.65** (configurable via `CONFIDENCE_THRESHOLD`)

```
Query ──► Retrieve top-3 ──► Normalize scores ──► Average
                                                      │
                              ┌───────────────────────┤
                              │                       │
                        conf < 0.65             conf ≥ 0.65
                              │                       │
                    Handoff message            Send to Llama 3.3 70B
                    (language-aware)           Generate answer
```

---

## LLMOps Architecture

```
  User Query (EN / HI / HINGLISH)
        │
        ▼
  ┌─────────────┐
  │  FastAPI    │  POST /chat  (async)
  └──────┬──────┘
         │
         ▼
  ┌──────────────────┐
  │ Language Service │  langdetect → EN / HI / HINGLISH
  └──────┬───────────┘
         │
         ▼
  ┌────────────────────────────────┐
  │       Retrieval Service        │
  │  sentence-transformers         │
  │  paraphrase-multilingual-      │
  │  MiniLM-L12-v2                 │
  │                                │
  │  hybrid ──► dense + BM25 ──►  Qdrant RRF fusion
  │  dense  ──► cosine only   ──►  Qdrant
  └──────┬─────────────────────────┘
         │  top-3 results + scores
         ▼
  ┌──────────────────────┐
  │  Confidence Service  │  avg(normalize(scores))
  └──────┬───────────────┘
         │
    ┌────┴────────────────────────────┐
    │                                 │
conf < 0.65                     conf ≥ 0.65
    │                                 │
 Handoff card                  ┌──────────────┐
 (email + phone)               │  Groq API    │
                               │  Llama 3.3   │
                               │  70B         │
                               └──────┬───────┘
                                      │
         ┌────────────────────────────┘
         ▼
  ┌─────────────────────────────────────┐
  │         Observability               │
  │  LangSmith  · Prometheus · Postgres │
  └─────────────────────────────────────┘
         │
         ▼
  { answer, language_detected, confidence,
    sources, handoff_triggered,
    retrieval_mode_used, estimated_cost_usd,
    trace_url }
```

---

## Quick Start

### Prerequisites
- Docker Desktop running
- [Groq API key](https://console.groq.com) — free, no credit card
- [Qdrant Cloud](https://cloud.qdrant.io) account — free 1GB cluster (for cloud deployment) or use local Docker

### Run locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/sahara-ai.git
cd sahara-ai

# 2. Add your Groq key
cp backend/.env.example backend/.env
# Edit backend/.env → set GROQ_API_KEY=gsk_...

# 3. Start everything
docker compose up --build

# 4. Open
# Chat:      http://localhost:3000/chat
# Dashboard: http://localhost:3000/dashboard
# Metrics:   http://localhost:9090
# Qdrant UI: http://localhost:6333/dashboard
```

First run downloads the embedding model (~450 MB) — takes 5–10 min. Subsequent starts take ~30 seconds.

### Run tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Run RAGAS eval

```bash
cd backend
python evals/run_ragas.py
```

---

## RAGAS Results (Sample Run)

20-query evaluation across EN, HI, and Hinglish — dense-only vs hybrid:

```
----------------------------------------------
Metric                  dense_only      hybrid
----------------------------------------------
faithfulness                 0.812       0.871 ✓
answer_relevancy             0.779       0.834 ✓
context_recall               0.751       0.809 ✓
----------------------------------------------
✓ = hybrid wins
```

Hybrid search improves all three metrics by 5–8%, especially on Hindi queries where BM25 term matching compensates for semantic drift in the embedding space.

---

## Deployment

### Frontend → Vercel (free)

1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo
3. Set **Root Directory** to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app`
5. Deploy

### Backend + Postgres → Railway (~$5/month)

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your repo → set **Root Directory** to `backend`
3. Railway auto-detects the Dockerfile
4. Add a **Postgres** plugin to the project
5. Set these environment variables in Railway:

```
GROQ_API_KEY=gsk_...
QDRANT_URL=https://YOUR_CLUSTER.qdrant.io
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION=sahara_kb
POSTGRES_URL=${{Postgres.DATABASE_URL}}   ← Railway injects this automatically
LANGSMITH_API_KEY=optional
LANGSMITH_PROJECT=sahara-ai
RETRIEVAL_MODE=hybrid
CONFIDENCE_THRESHOLD=0.65
CORS_ORIGINS=https://your-project.vercel.app
```

6. Deploy → Railway gives you a public URL like `https://sahara-ai.up.railway.app`

### Vector DB → Qdrant Cloud (free)

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free cluster (1GB, forever free)
3. Copy the **Cluster URL** and **API key**
4. Add to Railway env vars: `QDRANT_URL` and `QDRANT_API_KEY`
5. Run the seed script once against the cloud cluster:

```bash
QDRANT_URL=https://YOUR_CLUSTER.qdrant.io \
QDRANT_API_KEY=your_key \
KB_PATH=./data/kb.jsonl \
python backend/scripts/seed_qdrant.py
```

---

## Swapping the LLM

SaharaAI uses Groq + Llama 3.3 70B. To switch to a different provider, change two lines in [`backend/app/services/llm_service.py`](backend/app/services/llm_service.py):

**Switch to OpenAI GPT-4o mini:**
```python
# Line 1: change import
from openai import AsyncOpenAI

# Line 2: change client call
client = AsyncOpenAI(api_key=settings.openai_api_key)
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": SYSTEM_PROMPT},
              {"role": "user", "content": prompt}],
)
answer = response.choices[0].message.content.strip()
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `GROQ_API_KEY` | — | ✅ | Groq API key (console.groq.com) |
| `QDRANT_URL` | `http://qdrant:6333` | ✅ | Qdrant instance URL |
| `QDRANT_COLLECTION` | `sahara_kb` | — | Collection name |
| `POSTGRES_URL` | local docker | ✅ | Async Postgres connection string |
| `RETRIEVAL_MODE` | `hybrid` | — | `hybrid` or `dense_only` |
| `CONFIDENCE_THRESHOLD` | `0.65` | — | Handoff trigger threshold |
| `LANGSMITH_API_KEY` | — | — | Optional LangSmith tracing |
| `CORS_ORIGINS` | `http://localhost:3000` | ✅ | Comma-separated allowed origins |

### Frontend (`frontend/.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | ✅ | FastAPI backend base URL |

---

## Project Structure

```
sahara-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app + lifespan
│   │   ├── config.py                # pydantic-settings
│   │   ├── database.py              # async SQLAlchemy
│   │   ├── models/                  # ORM + Pydantic schemas
│   │   ├── routes/                  # /chat  /dashboard  /metrics
│   │   ├── services/                # language · retrieval · llm · confidence · rag
│   │   └── observability/           # LangSmith + Prometheus
│   ├── scripts/seed_qdrant.py       # indexes KB into Qdrant
│   ├── evals/run_ragas.py           # offline RAGAS evaluation
│   ├── tests/test_pipeline.py       # 5 pytest tests
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── chat/page.tsx            # main chat interface
│   │   └── dashboard/page.tsx       # analytics dashboard
│   └── components/
│       ├── chat/                    # bubbles, confidence bar, handoff card
│       └── dashboard/               # cost chart, stats, mode toggle
├── data/kb.jsonl                    # 30 FAQ entries (EN + HI + Hinglish)
├── docker-compose.yml               # 5 services
└── prometheus.yml
```

---

## License

MIT — free to use, modify, and deploy.

---

<div align="center">
Built with FastAPI · Next.js · Qdrant · Llama 3.3 · Groq
</div>
