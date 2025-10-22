FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/
COPY config/ ./config/

# Install SOLLOL
RUN pip install --no-cache-dir -e .

# Expose ports
EXPOSE 11434 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:11434/api/health', timeout=5)"

# Run SOLLOL (Drop-in replacement on Ollama's standard port)
CMD ["python", "-m", "sollol.cli", "up", "--workers", "4", "--port", "11434"]
