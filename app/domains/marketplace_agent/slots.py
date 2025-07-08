# app/domains/marketplace/slots.py

from typing import Dict
import re
import spacy

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except MemoryError:
    print("Not enough memory to load the spaCy model.")
  
# Regex patterns
PRODUCT_BUY_PATTERN = r"(?:beli|pesan|mau)\s+([\w\s\-+]+)"
PRODUCT_SELL_PATTERN = r"(?:jual|menjual|saya jual)\s+([\w\s\-+]+)"
CATEGORY_PATTERN = r"(?:promo|diskon|cari)\s+(?:produk|barang)?\s*(\w+)"
PRICE_PATTERN = r"(?:harga|seharga|dijual\s+seharga)\s*(\d+[.,]?\d*)"
QUANTITY_PATTERN = r"(\d+)\s*(pcs|buah|unit|kotak|pak|pasang)?"
LOCATION_PATTERN = r"(?:di|lokasi|kota)\s+([\w\s]+)"

def normalize(text: str) -> str:
    return text.lower().strip()

def extract_entities(message: str) -> Dict[str, list]:
    doc = nlp(message)
    return {
        "products": [ent.text for ent in doc.ents if ent.label_.lower() in ["product"]],
        "locations": [ent.text for ent in doc.ents if ent.label_.lower() in ["gpe", "loc"]],
    }

def extract_slots(intent: str, message: str) -> Dict[str, str]:
    slots = {}
    msg = normalize(message)
    ents = extract_entities(message)

    if intent == "buy_product":
        prod_match = re.search(PRODUCT_BUY_PATTERN, msg)
        qty_match = re.search(QUANTITY_PATTERN, msg)

        if prod_match:
            slots["product"] = prod_match.group(1).strip()
        elif ents["products"]:
            slots["product"] = ents["products"][0]

        if qty_match:
            slots["quantity"] = qty_match.group(1)

    elif intent == "sell_product":
        item_match = re.search(PRODUCT_SELL_PATTERN, msg)
        price_match = re.search(PRICE_PATTERN, msg)
        loc_match = re.search(LOCATION_PATTERN, msg)

        if item_match:
            slots["product"] = item_match.group(1).strip()
        elif ents["products"]:
            slots["product"] = ents["products"][0]

        if price_match:
            slots["price"] = price_match.group(1)

        if loc_match:
            slots["location"] = loc_match.group(1).strip()
        elif ents["locations"]:
            slots["location"] = ents["locations"][0]

    elif intent == "search_deals":
        category_match = re.search(CATEGORY_PATTERN, msg)
        if category_match:
            slots["category"] = category_match.group(1).strip()

    return slots
