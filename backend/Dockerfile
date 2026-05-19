FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model to avoid runtime delays
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Entrypoint: seed Qdrant then start the API
CMD ["sh", "-c", "python scripts/seed_qdrant.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
