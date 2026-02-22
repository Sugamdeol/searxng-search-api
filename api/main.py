"""
SearXNG Search API - FastAPI Wrapper
Self-hosted web search with 70+ engines, no API keys needed.
"""

import os
import json
import hashlib
from typing import Optional, List
from datetime import datetime
from functools import lru_cache

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Config
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")
REDIS_URL = os.getenv("REDIS_URL", "")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "100"))

# Init
app = FastAPI(
    title="SearXNG Search API",
    description="Self-hosted web search with 70+ engines",
    version="1.0.0"
)

# Redis setup (optional)
redis_client = None
if REDIS_URL:
    try:
        import redis as redis_lib
        redis_client = redis_lib.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
    except:
        redis_client = None

# In-memory cache fallback
_memory_cache = {}

def cache_get(key: str) -> Optional[str]:
    """Get from cache (Redis or memory)."""
    if redis_client:
        return redis_client.get(key)
    return _memory_cache.get(key)

def cache_set(key: str, value: str, ttl: int = 3600):
    """Set cache (Redis or memory)."""
    if redis_client:
        redis_client.setex(key, ttl, value)
    else:
        _memory_cache[key] = value

# Models
class SearchResult(BaseModel):
    title: str
    url: str
    content: Optional[str] = None
    engine: str
    score: Optional[float] = None
    publishedDate: Optional[str] = None
    thumbnail: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    time: float
    cached: bool = False
    engines: List[str]

class HealthResponse(BaseModel):
    status: str
    searxng: str
    redis: str
    timestamp: str

# Cache helper
def get_cache_key(query: str, category: str, **kwargs) -> str:
    """Generate cache key from query params."""
    key_data = f"{query}:{category}:{json.dumps(kwargs, sort_keys=True)}"
    return f"search:{hashlib.md5(key_data.encode()).hexdigest()}"

# Search helper
async def search_searxng(
    query: str,
    category: str = "general",
    limit: int = 10,
    safesearch: int = 1,
    language: str = "en"
) -> dict:
    """Query SearXNG instance."""
    
    params = {
        "q": query,
        "format": "json",
        "categories": category,
        "language": language,
        "safesearch": safesearch,
        "pageno": 1
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SEARXNG_URL}/search", params=params)
        response.raise_for_status()
        return response.json()

# Format results
def format_results(data: dict, category: str) -> List[SearchResult]:
    """Format SearXNG results to our schema."""
    results = []
    
    for r in data.get("results", []):
        result = SearchResult(
            title=r.get("title", "Untitled"),
            url=r.get("url", ""),
            content=r.get("content", r.get("abstract", "")),
            engine=r.get("engine", "unknown"),
            score=r.get("score"),
            publishedDate=r.get("publishedDate"),
            thumbnail=r.get("thumbnail") if category == "images" else None
        )
        results.append(result)
    
    return results

# Endpoints
@app.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=MAX_RESULTS, description="Number of results"),
    safesearch: int = Query(1, ge=0, le=2, description="0=off, 1=moderate, 2=strict"),
    language: str = Query("en", description="Language code (en, de, fr, etc.)")
):
    """General web search across all engines."""
    
    # Check cache
    cache_key = get_cache_key(q, "general", limit=limit, safesearch=safesearch, lang=language)
    cached = cache_get(cache_key)
    
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return SearchResponse(**data)
    
    # Fetch from SearXNG
    try:
        data = await search_searxng(q, "general", limit, safesearch, language)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(e)}")
    
    # Format response
    response_data = {
        "query": q,
        "results": format_results(data, "general")[:limit],
        "total": data.get("number_of_results", 0),
        "time": data.get("search_duration", 0),
        "cached": False,
        "engines": data.get("engines", [])
    }
    
    # Cache result
    cache_set(cache_key, json.dumps(response_data), CACHE_TTL)
    
    return SearchResponse(**response_data)

@app.get("/news", response_model=SearchResponse)
async def news(
    q: str = Query(..., description="News search query"),
    limit: int = Query(10, ge=1, le=MAX_RESULTS),
    safesearch: int = Query(1, ge=0, le=2),
    language: str = Query("en")
):
    """Search news articles."""
    
    cache_key = get_cache_key(q, "news", limit=limit, safesearch=safesearch, lang=language)
    cached = cache_get(cache_key)
    
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return SearchResponse(**data)
    
    try:
        data = await search_searxng(q, "news", limit, safesearch, language)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(e)}")
    
    response_data = {
        "query": q,
        "results": format_results(data, "news")[:limit],
        "total": data.get("number_of_results", 0),
        "time": data.get("search_duration", 0),
        "cached": False,
        "engines": data.get("engines", [])
    }
    
    cache_set(cache_key, json.dumps(response_data), CACHE_TTL)
    return SearchResponse(**response_data)

@app.get("/images", response_model=SearchResponse)
async def images(
    q: str = Query(..., description="Image search query"),
    limit: int = Query(20, ge=1, le=MAX_RESULTS),
    safesearch: int = Query(1, ge=0, le=2)
):
    """Search images."""
    
    cache_key = get_cache_key(q, "images", limit=limit, safesearch=safesearch)
    cached = cache_get(cache_key)
    
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return SearchResponse(**data)
    
    try:
        data = await search_searxng(q, "images", limit, safesearch)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(e)}")
    
    response_data = {
        "query": q,
        "results": format_results(data, "images")[:limit],
        "total": data.get("number_of_results", 0),
        "time": data.get("search_duration", 0),
        "cached": False,
        "engines": data.get("engines", [])
    }
    
    cache_set(cache_key, json.dumps(response_data), CACHE_TTL)
    return SearchResponse(**response_data)

@app.get("/videos", response_model=SearchResponse)
async def videos(
    q: str = Query(..., description="Video search query"),
    limit: int = Query(10, ge=1, le=MAX_RESULTS),
    safesearch: int = Query(1, ge=0, le=2)
):
    """Search videos."""
    
    cache_key = get_cache_key(q, "videos", limit=limit, safesearch=safesearch)
    cached = cache_get(cache_key)
    
    if cached:
        data = json.loads(cached)
        data["cached"] = True
        return SearchResponse(**data)
    
    try:
        data = await search_searxng(q, "videos", limit, safesearch)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Search service unavailable: {str(e)}")
    
    response_data = {
        "query": q,
        "results": format_results(data, "videos")[:limit],
        "total": data.get("number_of_results", 0),
        "time": data.get("search_duration", 0),
        "cached": False,
        "engines": data.get("engines", [])
    }
    
    cache_set(cache_key, json.dumps(response_data), CACHE_TTL)
    return SearchResponse(**response_data)

@app.get("/health", response_model=HealthResponse)
async def health():
    """Check service health."""
    
    searxng_status = "unknown"
    redis_status = "disabled" if not REDIS_URL else "unknown"
    
    # Check SearXNG
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SEARXNG_URL}/healthz")
            searxng_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        searxng_status = "unreachable"
    
    # Check Redis
    if REDIS_URL and redis_client:
        try:
            redis_client.ping()
            redis_status = "healthy"
        except:
            redis_status = "unreachable"
    
    overall = "healthy" if searxng_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall,
        searxng=searxng_status,
        redis=redis_status,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/")
async def root():
    """API info."""
    return {
        "name": "SearXNG Search API",
        "version": "1.0.0",
        "cache": "redis" if redis_client else "memory",
        "endpoints": [
            "/search - Web search",
            "/news - News search", 
            "/images - Image search",
            "/videos - Video search",
            "/health - Health check"
        ],
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
