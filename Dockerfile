# Unified SearXNG + FastAPI container for Render free tier
FROM python:3.11-slim

# Install SearXNG dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SearXNG
WORKDIR /searxng
RUN git clone --depth 1 https://github.com/searxng/searxng.git . \
    && pip install --no-cache-dir -e .

# Copy SearXNG settings
COPY searxng/settings.yml /etc/searxng/settings.yml

# Install FastAPI dependencies
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI app
COPY api/main.py .

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Environment variables
ENV SEARXNG_SETTINGS_PATH=/etc/searxng/settings.yml
ENV SEARXNG_SECRET=ultrasecretkey
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8080 8000

# Start both services
CMD ["/start.sh"]
