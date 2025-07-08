#app/rag_engine.py

from typing import List
import faiss
import numpy as np
import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

INDEX_PATH = "model/faiss_index.index"
DOCS_PATH = "model/documents.json"

index = None
metadata = []

def load_rag_index():
    global index, metadata
    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
        try:
            index = faiss.read_index(INDEX_PATH)
            with open(DOCS_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            print(f"[RAG] ✅ Loaded {len(metadata)} documents into FAISS index.")
        except Exception as e:
            print(f"[RAG] ❌ Failed to load index: {e}")
    else:
        print("[RAG] ⚠️ Index or metadata file not found.")

def retrieve(query: str, domain: str, user_id: str) -> List[str]:
    if not index or not metadata:
        return ["[RAG unavailable] No index found."]

    try:
        query_vec = model.encode([query])
        D, I = index.search(np.array(query_vec).astype("float32"), k=5)

        results = []
        for i in I[0]:
            if i < len(metadata):
                entry = metadata[i]
                if domain.lower() in entry.get("domain", "").lower():
                    content = entry.get("description") or entry.get("content", "")
                    results.append(content)
        return results or ["[No domain-specific RAG results found]"]
    except Exception as e:
        print(f"[RAG] ❌ Error during retrieval: {e}")
        return ["[RAG error] Could not complete retrieval."]

def format_rag_context(docs: List[str], domain: str) -> str:
    if not docs:
        return f"--- No {domain} context found ---"
    return f"--- {domain} Context ---\n" + "\n".join(f"- {doc}" for doc in docs)

# Load on startup
load_rag_index()
