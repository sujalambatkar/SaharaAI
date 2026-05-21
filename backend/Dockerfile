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

# Copy source code
COPY . .

# Bundle KB data so Railway (no volume mounts) can seed Qdrant at startup
COPY data/kb.jsonl /data/kb.jsonl

# Expose FastAPI port
EXPOSE 8000

# Entrypoint: seed Qdrant then start the API
CMD ["sh", "start.sh"]
