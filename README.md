
# 🤖 LocalLoop – Smart Commerce Agent  
### *AI Agent for Shopping, Travel, and Food*

**LocalLoop** is a **multilingual AI assistant** built to deliver intelligent, contextual, and personalized experiences across commercial domains such as **food**, **travel**, and **marketplaces**. Leveraging **RAG (Retrieval-Augmented Generation)**, **knowledge graphs**, and modular **agent orchestration**, LocalLoop enables users to interact via **text or voice** in both **English 🇬🇧** and **Indonesian 🇮🇩**.

---

## ✨ Key Features

- 🍽️ **Food Agent** – Discover restaurants, browse menus, and place orders  
- 🛫 **Travel Agent** – Search for flights, reserve hotels, and plan itineraries  
- 🛍️ **Marketplace Agent** – Buy or sell new and second-hand items  
- 🧠 **Knowledge Graph Profile** – Persistent and reusable user personalization  
- 🗣️ **Multimodal Interaction** – Text and voice input support  
- 🌐 **Multilingual Support** – English & Indonesian  

---

## 🧠 AI Architecture & Agent Design

### 🧩 Modular Agent Orchestration
- **Natural language-based intent & domain detection**
- **Dynamic fallback logic** tailored per domain
- **RAG-powered retrieval** with FAISS or Weaviate for contextual relevance

### 🔎 Domain Agents
- `FoodAgent`, `TravelAgent`, `MarketplaceAgent`  
- Manage slot filling, session memory, task execution, and fallbacks

### 🧬 Knowledge Graph Personalization
- RDF-based graph representing user preferences
- Built incrementally through in-app interactions
- Visualizable through a UI (`graph.html`)

---

## ⚙️ Tech Stack

| Component             | Description                                |
|----------------------|--------------------------------------------|
| **Groq + LLaMA 3.1** | High-speed, low-latency LLM inference      |
| **FAISS / Weaviate** | Vector-based retrieval for RAG             |
| **SERP API / Tavily**| Fallback web search                        |
| **Infobip**          | Voice and WhatsApp integration             |
| **LangChain**        | Orchestration, memory, and chaining        |
| **Flask**            | Lightweight web backend                    |

---

## ✅ Challenge Criteria Fulfilled

- ✅ Food ordering  
- ✅ Travel booking  
- ✅ Product marketplace  
- ✅ Voice-first & multimodal interface  
- ✅ Knowledge graph-based user profile  
- ✅ AI-powered recommendations  
- ✅ Reusable personalization across domains  
- ✅ Live demo–ready  
- ✅ Modular and scalable architecture  

---

## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/bambangirawans/localloop.git
cd localloop
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Then, add the following API keys to your `.env` file:

* `GROQ_API_KEY` – for LLaMA 3.1 via Groq
* `SERP_API_KEY` or `TAVILY_API_KEY` – for fallback search
* `INFOBIP_KEY` – for WhatsApp and voice integration

### 4. (Optional) Build FAISS Index

```bash
python scripts/build_faiss_index.py
```

### 5. Run the Application

```bash
python run.py
```

---

## 🌐 User Interface

| File               | Description                              |
| ------------------ | ---------------------------------------- |
| `index.html`       | Main chat interface                      |
| `graph.html`       | RDF user profile graph visualizer        |
| `voice_handler.py` | Voice input and speech recognition logic |

---

## 🧰 Useful Scripts

* `scripts/build_faiss_index.py` – Builds FAISS index from data
* `scripts/generate_rag_data_with_llm.py` – Auto-generates RAG knowledge base
* `scripts/visualize_graph.py` – Visualizes the user profile graph

---

## 🤝 Contributing

We welcome feedback, ideas, and contributions!

* 🐞 Please open an issue or pull request to contribute

---

## 🔖 License

MIT License © 2025 — LocalLoop Team

