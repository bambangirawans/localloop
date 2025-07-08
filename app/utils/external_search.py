# app/utils/external_search.py

import os
import requests

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

def use_tavily(query: str, num_results: int = 3) -> str | None:
    if not TAVILY_API_KEY:
        return None

    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "include_answers": False,
                "include_raw_content": False,
                "max_results": num_results
            }
        )
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None
        return "--- Web Search Results ---\n" + "\n".join(
            f"- {r.get('title')}: {r.get('content')}" for r in results if "content" in r
        )
    except Exception as e:
        return None

def use_serpapi_search(query: str) -> str | None:
    if not SERP_API_KEY:
        return None

    try:
        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "engine": "google",
            "num": 5
        }
        resp = requests.get("https://serpapi.com/search", params=params)
        data = resp.json()
        results = data.get("organic_results", [])
        if not results:
            return None

        return "--- Google Search ---\n" + "\n".join(
            f"- {r.get('title')}: {r.get('snippet')}" for r in results if "snippet" in r
        )
    except Exception as e:
        return None
