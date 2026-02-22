#!/bin/bash
set -e

# Generate random secret if not set
if [ -z "$SEARXNG_SECRET" ] || [ "$SEARXNG_SECRET" = "ultrasecretkey" ]; then
    export SEARXNG_SECRET=$(head -c 32 /dev/urandom | xxd -p | tr -d '\n')
    echo "Generated SearXNG secret"
fi

# Update settings.yml with secret
sed -i "s/ultrasecretkey/$SEARXNG_SECRET/g" /etc/searxng/settings.yml

# Start SearXNG in background
echo "Starting SearXNG..."
python -m searx.webapp &
SEARXNG_PID=$!

# Wait for SearXNG to be ready
echo "Waiting for SearXNG..."
for i in {1..30}; do
    if wget -q --spider http://localhost:8080/healthz 2>/dev/null; then
        echo "SearXNG is ready!"
        break
    fi
    sleep 1
done

# Set internal URL for FastAPI
export SEARXNG_URL=http://localhost:8080

# Start FastAPI
echo "Starting FastAPI..."
cd /app && exec uvicorn main:app --host 0.0.0.0 --port 8000
