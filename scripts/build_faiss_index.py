# scripts/build_faiss_index.py

import faiss
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

DATA_PATH = "data/rag_data.json"
INDEX_PATH = "model/faiss_index.index"
DOCS_PATH = "model/documents.json"

def build_index():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)

    texts = [entry["content"] for entry in entries]
    embeddings = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"✅ Built FAISS index with {len(entries)} documents")

if __name__ == "__main__":
    os.makedirs("model", exist_ok=True)
    build_index()
