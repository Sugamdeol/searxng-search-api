# searxng-search

Self-hosted web search API using SearXNG metasearch engine. Aggregates results from 70+ search engines without API keys or rate limits.

## Features

- **No API keys needed** - Uses SearXNG's distributed search
- **70+ search engines** - Google, Bing, DuckDuckGo, Wikipedia, etc.
- **Privacy-focused** - Self-hosted, no tracking
- **Multiple formats** - Web, news, images, videos
- **FastAPI wrapper** - Clean REST API with automatic docs
- **Redis caching** - Speed up repeated queries
- **One-click deploy** - Render/Railway ready

## Quick Start

### Local Development

```bash
# Start SearXNG + API
docker compose up -d

# Test search
curl "http://localhost:8080/search?q=python+tutorial"
```

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/searxng-search)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET | General web search |
| `/news` | GET | News search |
| `/images` | GET | Image search |
| `/videos` | GET | Video search |
| `/health` | GET | Service health check |

## Query Parameters

- `q` - Search query (required)
- `limit` - Number of results (default: 10, max: 100)
- `safesearch` - 0 (off), 1 (moderate), 2 (strict)
- `language` - Language code (en, de, fr, etc.)

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
  "time": 0.45
}
```

## Architecture

```
User → FastAPI → SearXNG → 70+ Search Engines
         ↓
      Redis Cache
```

## Files

- `docker-compose.yml` - SearXNG + Valkey + API stack
- `api/main.py` - FastAPI wrapper
- `searxng/settings.yml` - SearXNG configuration
- `render.yaml` - Render deployment spec

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_HOST` | `http://searxng:8080` | SearXNG internal URL |
| `REDIS_URL` | `redis://redis:6379` | Redis cache URL |
| `CACHE_TTL` | `3600` | Cache time in seconds |
| `MAX_RESULTS` | `100` | Max results per query |

## Usage Examples

### Basic Search
```python
import requests

response = requests.get("http://localhost:8080/search?q=machine+learning")
data = response.json()
for result in data["results"]:
    print(f"{result['title']}: {result['url']}")
```

### With Options
```bash
curl "http://localhost:8080/search?q=news&limit=20&language=en&safesearch=1"
```

## Maintenance

Update SearXNG:
```bash
docker compose pull
docker compose up -d
```

View logs:
```bash
docker compose logs -f searxng
docker compose logs -f api
```

## License

AGPL-3.0 (same as SearXNG)
