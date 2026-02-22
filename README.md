# SearXNG Search API

Self-hosted web search API with 70+ engines. No API keys. No rate limits. Full privacy.

## Quick Start

### Local (Unified Container)
```bash
# Clone and build
git clone https://github.com/yourusername/searxng-search.git
cd searxng-search
docker build -t searxng-search .

# Run
docker run -p 8000:8000 -e SEARXNG_SECRET=$(openssl rand -hex 32) searxng-search

# Test
curl "http://localhost:8000/search?q=python+tutorial"
```

### Local (Docker Compose - Development)
```bash
# Set secret key
sed -i "s|ultrasecretkey|$(openssl rand -hex 32)|g" searxng/settings.yml

# Start all services
docker compose up -d
```

## Deploy to Render (Free Tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Sugamdeol/searxng-search-api)

**Single container** with both SearXNG + FastAPI (optimized for Render's 512MB free tier). No Redis needed - uses in-memory caching.

## API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /search?q=query` | Web search | `/search?q=machine+learning` |
| `GET /news?q=query` | News articles | `/news?q=tech+startups` |
| `GET /images?q=query` | Image search | `/images?q=cats&limit=20` |
| `GET /videos?q=query` | Video search | `/videos?q=tutorials` |
| `GET /health` | Health check | `/health` |

### Query Parameters

- `q` - Search query (required)
- `limit` - Results count (default: 10, max: 100)
- `safesearch` - 0 (off), 1 (moderate), 2 (strict)
- `language` - Language code: en, de, fr, es, etc.

## Response Format

```json
{
  "query": "python tutorial",
  "results": [
    {
      "title": "Python Tutorial - W3Schools",
      "url": "https://www.w3schools.com/python/",
      "content": "Learn Python with W3Schools...",
      "engine": "google",
      "score": 0.95
    }
  ],
  "total": 1500000,
  "time": 0.45,
  "cached": false,
  "engines": ["google", "duckduckgo", "bing"]
}
```

## Usage Examples

### Python
```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={"q": "machine learning", "limit": 5}
)
data = response.json()

for result in data["results"]:
    print(f"{result['title']}: {result['url']}")
```

### cURL
```bash
curl "http://localhost:8000/search?q=news&limit=20&language=en"
```

### JavaScript
```javascript
const response = await fetch(
  'http://localhost:8000/search?q=javascript+frameworks'
);
const data = await response.json();
console.log(data.results);
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Client    │────▶│  FastAPI    │────▶│    SearXNG      │
│             │     │   Wrapper   │     │  (70+ engines)  │
└─────────────┘     └──────┬──────┘     └─────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │    Cache    │
                    └─────────────┘
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_URL` | `http://searxng:8080` | SearXNG internal URL |
| `REDIS_URL` | `redis://redis:6379` | Redis connection |
| `CACHE_TTL` | `3600` | Cache time (seconds) |
| `MAX_RESULTS` | `100` | Max results per query |

## Maintenance

```bash
# View logs
docker compose logs -f

# Update SearXNG
docker compose pull
docker compose up -d

# Clear cache
docker compose exec redis redis-cli FLUSHDB

# Restart
docker compose restart
```

## Why This?

| Feature | Google API | Bing API | SearXNG API |
|---------|-----------|----------|-------------|
| API Key | Required | Required | **None** |
| Rate Limits | 100/day | 1000/mo | **Unlimited** |
| Cost | $5/1000 | $7/1000 | **Free** |
| Privacy | Tracked | Tracked | **Private** |
| Engines | 1 | 1 | **70+** |

## License

AGPL-3.0 (same as SearXNG)
