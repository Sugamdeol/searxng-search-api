# searxng-search

Web search using public SearXNG instances. Aggregates results from 70+ search engines without API keys.

## Features

- **No API keys needed** - Uses public SearXNG instances
- **70+ search engines** - Google, Bing, DuckDuckGo, Wikipedia, etc.
- **Privacy-focused** - No tracking, no self-hosting required
- **Multiple formats** - Web, news, images, videos
- **FastAPI wrapper** - Clean REST API with auto-fallback
- **Instance rotation** - Auto-switches if one instance is down

## Quick Start

### Option 1: Use Directly (No Deploy)

```python
import requests

# Call public SearXNG instance directly
response = requests.get(
    "https://search.sapti.me/search",
    params={"q": "python tutorial", "format": "json"}
)
data = response.json()
```

### Option 2: Deploy Your Own Wrapper

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Sugamdeol/searxng-search-api)

## Public SearXNG Instances

| Instance | URL | Location |
|----------|-----|----------|
| search.sapti.me | https://search.sapti.me | EU |
| searx.be | https://searx.be | EU |
| search.bus-hit.me | https://search.bus-hit.me | EU |
| searx.drgns.space | https://searx.drgns.space | US |
| searx.oakleycord.dev | https://searx.oakleycord.dev | US |

## API Endpoints (If Self-Hosted)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | GET | General web search |
| `/news` | GET | News search |
| `/images` | GET | Image search |
| `/videos` | GET | Video search |
| `/health` | GET | Service health check |

## Direct SearXNG API Format

```bash
# Basic search
curl "https://search.sapti.me/search?q=python+tutorial&format=json"

# News only
curl "https://search.sapti.me/search?q=tech+news&categories=news&format=json"

# Images
curl "https://search.sapti.me/search?q=cats&categories=images&format=json"
```

## Response Format

```json
{
  "query": "python tutorial",
  "number_of_results": 1500000,
  "results": [
    {
      "title": "Python Tutorial - W3Schools",
      "url": "https://www.w3schools.com/python/",
      "content": "Learn Python with W3Schools...",
      "engine": "google"
    }
  ]
}
```

## Python Usage

```python
import requests

def search_web(query, instance="https://search.sapti.me"):
    """Search using public SearXNG instance"""
    response = requests.get(
        f"{instance}/search",
        params={"q": query, "format": "json"},
        timeout=30
    )
    return response.json()

# Search
results = search_web("machine learning tutorial")
for r in results["results"][:5]:
    print(f"{r['title']}: {r['url']}")
```

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `q` | Search query | required |
| `format` | Output format (json, html) | html |
| `categories` | Filter by category (general, news, images, videos) | general |
| `language` | Language code (en, de, fr, etc.) | en |
| `safesearch` | Safe search (0=off, 1=moderate, 2=strict) | 1 |
| `pageno` | Page number | 1 |

## Files

- `api/main.py` - FastAPI wrapper with fallback instances
- `render.yaml` - Render deployment spec
- `requirements.txt` - Python dependencies

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_INSTANCES` | Comma-separated list | Fallback instances |
| `DEFAULT_INSTANCE` | `https://search.sapti.me` | Primary instance |

## License

AGPL-3.0 (same as SearXNG)
