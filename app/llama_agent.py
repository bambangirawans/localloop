# app/llama_agent.py
import os
from openai import OpenAI
from langdetect import detect
from app.rag_engine import retrieve, format_rag_context
from app.intents.intent_classifier import classify_intent
from app.utils.domain_detector import detect_domain
from app.utils.user_graph import user_graph

client = OpenAI(
    api_key=os.getenv("GROG_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL_NAME = "llama3-8b-8192"


def ask_llama(prompt: str, temperature: float = 0.3) -> str:
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Sorry, AI connection failed."

