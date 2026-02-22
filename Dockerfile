FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for SearXNG
WORKDIR /searxng

# Clone SearXNG
RUN git clone --depth 1 https://github.com/searxng/searxng.git .

# Install SearXNG dependencies first (including msgspec)
RUN pip install --no-cache-dir \
    msgspec \
    babel \
    flask \
    jinja2 \
    lxml \
    pyyaml \
    requests \
    httpx \
    uvloop \
    brotli \
    aiohttp \
    certifi

# Now install SearXNG in editable mode
RUN pip install --no-cache-dir -e .

# Copy SearXNG settings
COPY searxng/settings.yml /etc/searxng/settings.yml

# Set working directory for FastAPI
WORKDIR /app

# Copy FastAPI requirements and install
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI code
COPY api/ .

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8080

# Start both services
CMD ["./start.sh"]
