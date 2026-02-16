FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Set working directory
WORKDIR /app

# Install dependencies first for caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Make scripts executable
RUN chmod +x scripts/*.sh

# Default command using a shell to run prestart script then start the server
CMD ["sh", "-c", "scripts/prestart.sh && fastapi run app/main.py --port 8000 --host 0.0.0.0"]
