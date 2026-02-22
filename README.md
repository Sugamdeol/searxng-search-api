# SearXNG Search API

Lightweight web search API using public SearXNG instances. Deploys on Render free tier.

## Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Sugamdeol/searxng-search-api)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /search?q=query` | Web search |
| `GET /news?q=query` | News search |
| `GET /images?q=query` | Image search |
| `GET /videos?q=query` | Video search |
| `GET /health` | Health check |
| `GET /docs` | Auto-generated docs |

## Example

```bash
curl "https://your-service.onrender.com/search?q=python+tutorial"
```

## How It Works

- Uses 8 public SearXNG instances as fallback
- Auto-switches if one instance fails
- Returns JSON results from 70+ search engines
