# Dockerfile
# Stage 1: Build dependencies
FROM python:3.10-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels .

# Stage 2: Runtime
FROM python:3.10-slim

# System dependencies for ChromaDB/SQLite
RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN useradd -m -s /bin/bash proxyuser

# Copy built wheels and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .
RUN chown -R proxyuser:proxyuser /app

USER proxyuser

# Default network configuration (overridable via 'docker run -e')
# host.docker.internal allows the container to talk to the local host's Ollama instance
ENV OLLAMA_API_BASE_URL="http://host.docker.internal:11434"
ENV PORT=8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]