#!/usr/bin/env python3
"""
Test script for SearXNG Search API
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    data = r.json()
    print(f"  Status: {data['status']}")
    print(f"  SearXNG: {data['searxng']}")
    print(f"  Redis: {data['redis']}")
    assert r.status_code == 200
    print("  ✓ Health check passed\n")

def test_search():
    """Test search endpoint."""
    print("Testing /search?q=python...")
    r = requests.get(f"{BASE_URL}/search", params={"q": "python tutorial", "limit": 3})
    data = r.json()
    print(f"  Query: {data['query']}")
    print(f"  Results: {len(data['results'])}")
    print(f"  Engines: {', '.join(data['engines'][:3])}")
    assert len(data['results']) > 0
    print("  ✓ Search passed\n")

def test_news():
    """Test news endpoint."""
    print("Testing /news?q=tech...")
    r = requests.get(f"{BASE_URL}/news", params={"q": "technology", "limit": 3})
    data = r.json()
    print(f"  Query: {data['query']}")
    print(f"  Results: {len(data['results'])}")
    assert r.status_code == 200
    print("  ✓ News passed\n")

def test_images():
    """Test images endpoint."""
    print("Testing /images?q=cat...")
    r = requests.get(f"{BASE_URL}/images", params={"q": "cat", "limit": 3})
    data = r.json()
    print(f"  Query: {data['query']}")
    print(f"  Results: {len(data['results'])}")
    assert r.status_code == 200
    print("  ✓ Images passed\n")

def test_videos():
    """Test videos endpoint."""
    print("Testing /videos?q=music...")
    r = requests.get(f"{BASE_URL}/videos", params={"q": "music", "limit": 3})
    data = r.json()
    print(f"  Query: {data['query']}")
    print(f"  Results: {len(data['results'])}")
    assert r.status_code == 200
    print("  ✓ Videos passed\n")

def test_cached():
    """Test caching."""
    print("Testing cache...")
    # First request
    r1 = requests.get(f"{BASE_URL}/search", params={"q": "cache test", "limit": 1})
    data1 = r1.json()
    
    # Second request (should be cached)
    r2 = requests.get(f"{BASE_URL}/search", params={"q": "cache test", "limit": 1})
    data2 = r2.json()
    
    print(f"  First request cached: {data1['cached']}")
    print(f"  Second request cached: {data2['cached']}")
    assert data1['cached'] == False
    assert data2['cached'] == True
    print("  ✓ Cache working\n")

if __name__ == "__main__":
    print("="*50)
    print("SearXNG Search API Tests")
    print("="*50 + "\n")
    
    try:
        test_health()
        test_search()
        test_news()
        test_images()
        test_videos()
        test_cached()
        
        print("="*50)
        print("All tests passed! ✓")
        print("="*50)
        
    except requests.ConnectionError:
        print("\n✗ Error: Cannot connect to API")
        print(f"Make sure services are running: docker compose up -d")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
