# app/domains/food_agent/slots.py

import os
import requests
import re
from typing import Dict, List
from difflib import get_close_matches
import spacy
from sentence_transformers import SentenceTransformer, util

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except Exception as e:
    print(f"spaCy load failed: {e}")
    nlp = None

embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

QUANTITY_ITEM_PATTERN = r"(?:(\d{1,2})\s*(?:x|porsi|pcs|buah|gelas|mangkuk|kotak|bungkus|plates|units)?\s*)?([\w\s\-]+?)(?=(?:dan|,|&|$))"
TIME_PATTERN = r"(?:jam|pukul|at|sekitar|around)?\s*(\d{1,2})([:.]?(\d{2}))?\s*(pagi|siang|sore|malam|am|pm)?"
LOCATION_PATTERN = r"(?:di|near|sekitar|area)\s+([\w\s]+)"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  

def get_image_url(query: str) -> str:
    if not TAVILY_API_KEY:
        print("[get_image_url] Tavily API key not set.")
        return None

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": TAVILY_API_KEY,
                "query": f"{query} food image",
                "search_depth": "basic",
                "include_images": True,
                "max_results": 1,
            },
            timeout=5
        )
        data = response.json()

        if "images" in data and data["images"]:
            image_result = data["images"][0]
            if isinstance(image_result, dict):
                return image_result.get("url")
            elif isinstance(image_result, str):
                return image_result
            else:
                print("[get_image_url] Unexpected image result format:", image_result)
    except Exception as e:
        print(f"[get_image_url] Error: {e}")
    return None

    
def normalize_text(text: str) -> str:
    return text.lower().strip()

def match_food_item(fragment: str, reference_items: List[str] = None) -> str:
    fragment = normalize_text(fragment)
    if not reference_items:
        return fragment  

    try:
        emb_input = embedding_model.encode(fragment, convert_to_tensor=True)
        emb_list = embedding_model.encode(reference_items, convert_to_tensor=True)
        scores = util.cos_sim(emb_input, emb_list)[0]
        best_idx = scores.argmax().item()
        return reference_items[best_idx]
    except Exception as e:
        print("[match_food_item] Error:", e)
        return fragment

def extract_with_spacy(message: str) -> Dict[str, List[str]]:
    doc = nlp(message)
    entities = {"food_candidates": [], "locations": []}

    for ent in doc.ents:
        label = ent.label_.lower()
        if label in ["loc", "gpe"]:
            entities["locations"].append(ent.text.strip())
        elif label in ["product", "org", "misc", "food"]:
            entities["food_candidates"].append(ent.text.strip())

    return entities

def extract_slots(intent: str, message: str) -> Dict[str, object]:
    slots = {}
    msg = normalize_text(message)

    spacy_ents = extract_with_spacy(message) if nlp else {"food_candidates": [], "locations": []}

    if intent in ["order_food", "add_to_order"]:
        items = re.findall(QUANTITY_ITEM_PATTERN, msg)
        order_list = []

        for qty, raw_item in items:
            raw_item = raw_item.strip()
            if not raw_item:
                continue
            candidate = match_food_item(raw_item, spacy_ents["food_candidates"])
            order_list.append({
                "item": candidate,
                "quantity": qty or "1",
                "image_url": get_image_url(candidate)
            })

        existing_items = [o["item"].lower() for o in order_list]
        for ent in spacy_ents["food_candidates"]:
            if ent.lower() not in existing_items:
                candidate = match_food_item(ent)
                order_list.append({
                    "item": candidate,
                    "quantity": "1",
                    "image_url": get_image_url(candidate)
                })


        if order_list:
            slots["orders"] = order_list

        time_match = re.search(TIME_PATTERN, msg)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(3) or "00"
            period = time_match.group(4) or ""
            slots["delivery_time"] = f"{hour}:{minute} {period}".strip()

    elif intent in ["find_restaurant", "restaurant_info"]:
        loc_match = re.search(LOCATION_PATTERN, msg)
        if loc_match:
            slots["location"] = loc_match.group(1).strip()
        elif spacy_ents["locations"]:
            slots["location"] = spacy_ents["locations"][0]

    return slots
