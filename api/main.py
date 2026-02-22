"""
SearXNG Search API - Uses public instances
Lightweight wrapper around public SearXNG instances
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random
from typing import List, Optional

app = FastAPI(
    title="SearXNG Search API",
    description="Web search using public SearXNG instances",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single reliable instance
SEARXNG_INSTANCES = [
    "https://searx.ox2.fr",           # 0.195s, 99% uptime, A+ grade
]

async def search_instance(instance: str, query: str, category: str = "general", 
                          language: str = "en", safesearch: int = 1):
    """Search a single SearXNG instance"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "q": query,
                "format": "json",
                "language": language,
                "safesearch": safesearch,
            }
            if category != "general":
                params["category"] = category
                
            response = await client.get(f"{instance}/search", params=params)
            
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None

async def search_with_fallback(query: str, category: str = "general",
                                  language: str = "en", safesearch: int = 1):
    """Try multiple instances until one works"""
    # Shuffle instances for load balancing
    instances = SEARXNG_INSTANCES.copy()
    random.shuffle(instances)
    
    errors = []
    for instance in instances[:5]:  # Try first 5
        result = await search_instance(instance, query, category, language, safesearch)
        if result:
            # Add metadata
            result["_instance_used"] = instance
            return result
        errors.append(f"{instance}: failed")
    
    raise HTTPException(status_code=503, detail=f"All instances failed. Errors: {errors}")

@app.get("/")
async def root():
    return {
        "message": "SearXNG Search API",
        "docs": "/docs",
        "endpoints": ["/search", "/news", "/images", "/videos", "/health"]
    }

@app.get("/health")
async def health():
    """Check if at least one instance is working"""
    for instance in SEARXNG_INSTANCES[:3]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{instance}/healthz")
                if response.status_code in [200, 404]:  # 404 is OK, means SearXNG is there
                    return {
                        "status": "healthy",
                        "instance": instance,
                        "available_instances": len(SEARXNG_INSTANCES)
                    }
        except:
            continue
    
    return {
        "status": "degraded",
        "message": "Some instances may be unavailable",
        "available_instances": len(SEARXNG_INSTANCES)
    }

@app.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    language: str = Query("en", description="Language code"),
    safesearch: int = Query(1, ge=0, le=2, description="Safe search level")
):
    """General web search"""
    results = await search_with_fallback(q, "general", language, safesearch)
    
    # Limit results
    if "results" in results:
        results["results"] = results["results"][:limit]
    
    return results

@app.get("/news")
async def news(
    q: str = Query(..., description="News search query"),
    limit: int = Query(10, ge=1, le=100),
    language: str = Query("en"),
    safesearch: int = Query(1, ge=0, le=2)
):
    """News search"""
    results = await search_with_fallback(q, "news", language, safesearch)
    
    if "results" in results:
        results["results"] = results["results"][:limit]
    
    return results

@app.get("/images")
async def images(
    q: str = Query(..., description="Image search query"),
    limit: int = Query(20, ge=1, le=100),
    language: str = Query("en"),
    safesearch: int = Query(1, ge=0, le=2)
):
    """Image search"""
    results = await search_with_fallback(q, "images", language, safesearch)
    
    if "results" in results:
        results["results"] = results["results"][:limit]
    
    return results

@app.get("/videos")
async def videos(
    q: str = Query(..., description="Video search query"),
    limit: int = Query(10, ge=1, le=100),
    language: str = Query("en"),
    safesearch: int = Query(1, ge=0, le=2)
):
    """Video search"""
    results = await search_with_fallback(q, "videos", language, safesearch)
    
    if "results" in results:
        results["results"] = results["results"][:limit]
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
