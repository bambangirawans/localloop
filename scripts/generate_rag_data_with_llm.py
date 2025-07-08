import os
import json
import requests
from openai import OpenAI

SERP_API_KEY = os.getenv("SERP_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
client = OpenAI(
    api_key=os.getenv("GROG_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
MODEL_NAME = "llama3-8b-8192"

def call_serp_api(query, num=5):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "hl": "id",
        "gl": "id",
        "num": num,
        "api_key": SERP_API_KEY
    }
    res = requests.get(url, params=params)
    return res.json().get("organic_results", [])

def extract_rag_items_with_llm(serp_results, query, domain):
    serp_texts = [r.get("title", "") + ": " + r.get("snippet", "") for r in serp_results if r.get("snippet")]

    system = f"""
You are an assistant that extracts structured RAG (retrieval-augmented generation) entries from web search results. 
Given a list of web snippets and a user intent ("{query}"), extract relevant items for the domain: {domain}.
Each item must contain: domain, title, description, location, and list of tags.
"""

    function_def = {
        "name": "add_rag_items",
        "description": "Extracts structured RAG knowledge items",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "location": {"type": "string"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["domain", "title", "description", "location", "tags"]
                    }
                }
            },
            "required": ["items"]
        }
    }

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "\n\n".join(serp_texts)}
        ],
        functions=[function_def],
        function_call={"name": "add_rag_items"},
        temperature=0.2,
    )

    result = response.choices[0].message.function_call.arguments
    return json.loads(result)["items"]

def load_queries(path="data/queries.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_rag_data():
    queries = load_queries()
    all_items = []

    for domain, query_list in queries.items():
        for query in query_list:
            print(f"🔍 Searching: {query}")
            serp = call_serp_api(query)

            # Optional fallback: use Tavily if SERP empty
            if not serp:
                print("⚠️ No SERP results, trying Tavily...")
                serp = call_tavily_api(query)  

            if not serp:
                print(f"⚠️ Skipping: no results from any provider.")
                continue

            try:
                items = extract_rag_items_with_llm(serp, query, domain)
                all_items.extend(items)
                print(f"✅ Parsed {len(items)} items from {query}")
            except Exception as e:
                print(f"❌ Error parsing {query}: {e}")


    for item in all_items:
        item["content"] = f"{item['title']} - {item['description']} (Location: {item['location']})"

    os.makedirs("data", exist_ok=True)
    with open("data/rag_data.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)

    print(f"\n📦 Saved {len(all_items)} RAG items to data/rag_data.json")

def call_tavily_api(query, num=5):
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    payload = {
        "query": query,
        "search_depth": "advanced",
        "include_answer": False,
        "include_raw_content": True
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        results = res.json().get("results", [])
        return [{"title": r["title"], "snippet": r.get("content", "")} for r in results][:num]
    except Exception as e:
        print("❌ Tavily error:", e)
        return []
    
if __name__ == "__main__":
    generate_rag_data()
