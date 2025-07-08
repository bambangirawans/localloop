#app/agent_orchestrator.py

import time
import torch
from importlib import import_module
from googletrans import Translator
from sentence_transformers import SentenceTransformer, util

from app.knowledge_graph import update_user_profile, build_context_prompt
from app.rag_engine import retrieve, format_rag_context
from app.llama_agent import ask_llama
from app.lang_detect import detect_language
from app.task_flow import get_task_stage, get_next_stage
from app.utils.user_graph import get_user_preference_tags
from app.utils.external_search import use_tavily, use_serpapi_search
from app.utils.session_memory import (
    remember_intent, get_last_intent, get_last_slots,
    clear_session, get_last_interaction_time,
    update_user_context, get_user_context, is_session_expired
)
from app.utils.context_followup import is_contextual_followup, get_contextual_prompt
from app.utils.domain_detector import detect_domain
from app.intents.intent_classifier import classify_intent
import app.utils.user_graph as user_graph

translator = Translator()
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

DOMAIN_MODULES = {
    "food": import_module("app.domains.food_agent"),
    "travel": import_module("app.domains.travel_agent"),
    "marketplace": import_module("app.domains.marketplace_agent")
}

RESET_PHRASES = [
    "mulai ulang", "reset sesi", "mulai dari awal", "hapus percakapan", "start over",
    "restart session", "clear chat", "reset everything", "ulang dari awal", "reset percakapan"
]
RESET_EMBEDDINGS = embedding_model.encode(RESET_PHRASES, convert_to_tensor=True)


def personalize_response(user_id: str, lang: str, domain: str) -> str:
    prefs = get_user_preference_tags(user_id)
    if not prefs:
        return ""

    matched_prefs = [
        pref for pref in prefs if detect_domain(pref, threshold=0.55, top_k=1) == domain
    ]

    if matched_prefs:
        joined = ", ".join(matched_prefs)
        return {
            "id": f"🤖 Berdasarkan preferensimu untuk {joined}, ini mungkin pas banget buatmu!",
            "en": f"🤖 Based on your interest in {joined}, this might be a perfect match for you!"
        }.get(lang, "")
    return ""


def run_orchestrated_agent(message: str, user_id: str = "anonymous_user", mode: str = "text") -> str:
    if not message.strip():
        return "❗ Please enter valid message."

    # Reset by user input
    input_vec = embedding_model.encode(message, convert_to_tensor=True)
    scores = util.cos_sim(input_vec, RESET_EMBEDDINGS)[0]
    if torch.max(scores).item() > 0.75:
        lang = detect_language(message)
        clear_session(user_id)
        return {
            "id": "🔄 Sesi kamu sudah direset. Yuk mulai dari awal!",
            "en": "🔄 Your session has been reset. Feel free to start fresh!"
        }.get(lang, "🔄 Session cleared.")

    if is_session_expired(user_id):
        clear_session(user_id)

    session_ctx = get_user_context(user_id)
    prev_lang = session_ctx.get("lang")
    prev_domain = session_ctx.get("domain")

    lang = prev_lang or detect_language(message)
    domain = prev_domain or detect_domain(message)

    print(f"[Orchestrator] Domain detected: {domain}")

    if prev_domain and domain != prev_domain and "general" not in (domain, prev_domain):
        clear_session(user_id)

    update_user_context(user_id, {"lang": lang, "domain": domain})
    update_user_profile(user_id, message)

    guessed_intent = classify_intent(message)
    if domain == "general" and guessed_intent:
        if any(kw in guessed_intent for kw in ["order", "food"]):
            domain = "food"
        elif any(kw in guessed_intent for kw in ["hotel", "travel"]):
            domain = "travel"
        elif any(kw in guessed_intent for kw in ["buy", "item"]):
            domain = "marketplace"

    handler = DOMAIN_MODULES.get(domain)
    if not handler:
        return default_fallback(message)

    if is_contextual_followup(message, user_id, mode):
        contextual_prompt = get_contextual_prompt(user_id)
        response = ask_llama(f"{contextual_prompt}\nUser: {message}\nAssistant:")
        return format_final_response(response, lang, user_id, domain, message)

    final_prompt = build_llm_prompt(message, user_id, domain)
 
    response = ask_llama(final_prompt)
 
    detected_intent = classify_intent(message, mode=mode)
    slots = handler.slots.extract_slots(detected_intent, message) if detected_intent else {}

    if detected_intent:
        remember_intent(user_id, detected_intent, slots)
        if hasattr(handler, "handle"):
            return handler.handle(detected_intent, slots, user_id)

    if not detected_intent:
        print("[Intent] Tidak ada intent jelas. Gunakan external search.")
        external_info = enrich_with_external_search(message)
        return format_final_response("🔍 Let me find the answer for you..." + external_info, lang, user_id, domain, message)

    if any(kw in response.lower() for kw in ["maaf", "tidak paham", "sorry", "don't understand"]):
        if hasattr(handler, "fallback"):
            return handler.fallback.fallback(message)
        return default_fallback(message)

    try:
        if detect_language(response) != lang:
            response = translator.translate(response, dest=lang).text
    except Exception as e:
        print("[Translation] Error:", e)

    return format_final_response(response, lang, user_id, domain, message)


def format_final_response(response: str, lang: str, user_id: str, domain: str, message: str) -> str:
    tone = {
        "id": "✨ Ini yang bisa saya bantu:",
        "en": "✨ Here's something that might help:"
    }.get(lang, "✅ Here's what I found:")

    personalization = personalize_response(user_id, lang, domain)
    stage = get_task_stage(message)
    dynamic_closing = get_next_stage(stage, domain, lang)

    response = response.strip()
    if len(response.split()) < 8 and not response.endswith("."):
        response += "."

    sections = [tone]
    if personalization:
        sections.append(personalization)
    sections.append(response)
    if dynamic_closing:
        sections.append(dynamic_closing)

    return "\n\n".join(sections).strip()


def enrich_with_external_search_original(query: str) -> str:
    tavily_result = use_tavily(query)
    serpapi_result = use_serpapi_search(query)

    if not tavily_result and not serpapi_result:
        return ""

    return f"\n\n🔍 Extra info:\n{tavily_result}\n{serpapi_result}".strip()


def default_fallback(message: str) -> str:
    lang = detect_language(message)
    return (
        "Maaf, saya belum yakin dengan maksud Anda. Bisa dijelaskan lagi?"
        if lang == "id"
        else "Sorry, I'm not sure what you meant. Could you please clarify?"
    )

def enrich_with_external_search(query: str) -> str:
 
    tavily_result = use_tavily(query)
    serpapi_result = use_serpapi_search(query)

    if not tavily_result and not serpapi_result:
        return ""


    combined_results = ""
    if tavily_result:
        combined_results += f"Tavily:\n{tavily_result.strip()}\n\n"
    if serpapi_result:
        combined_results += f"SERP:\n{serpapi_result.strip()}\n"

     reformulation_prompt = (
        f"You are a helpful assistant. A user asked a question and external sources returned raw information.\n"
        f"Your task is to rewrite and summarize the information into a clear, relevant, and natural-sounding response to the user's question.\n\n"
        f"User question: {query}\n\n"
        f"Raw external info:\n{combined_results.strip()}\n\n"
        f"Write a helpful, concise response to the user using only what's relevant from the info above."
    )

    refined_response = ask_llama(reformulation_prompt).strip()
    if not refined_response or "no useful" in refined_response.lower():
        return ""

    return f"\n\n🔍 Extra info:\n{refined_response}"


def build_llm_prompt(message: str, user_id: str, domain: str) -> str:
    context_kg = build_context_prompt(user_id)
    rag_context = format_rag_context(retrieve(message, domain, user_id), domain.upper())
    prefs = get_user_preference_tags(user_id)
    searches = user_graph.get_recent_searches(user_id)
    lang = user_graph.get_user_language(user_id)

    user_context = ""
    if prefs:
        user_context += f"User preferences: {', '.join(prefs)}\n"
    if searches:
        user_context += f"Recent searches: {', '.join(searches)}\n"
    if lang:
        user_context += f"Language: {lang}\n"

    return f"{user_context}\n{context_kg}\n{rag_context}\n\nUser: {message}\nAssistant:".strip()
