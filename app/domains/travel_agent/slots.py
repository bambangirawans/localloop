# app/domains/travel/slots.py

from typing import Dict
import re
import spacy
import dateparser

try:
    nlp = spacy.load("xx_ent_wiki_sm")
except MemoryError:
    print("Not enough memory to load the spaCy model.")

DATE_PATTERN = r"(hari\s+\w+|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|besok|lusa|hari ini)"
NIGHT_PATTERN = r"(\d{1,2})\s*(malam|malamnya|night|nights)"
FROM_PATTERN = r"(?:dari|asal)\s+([\w\s]+)"
TO_PATTERN = r"(?:ke|tujuan)\s+([\w\s]+)"
LOC_PATTERN = r"(?:di|ke|sekitar)\s+([\w\s]+)"

def normalize(text: str) -> str:
    return text.lower().strip()

def extract_entities(message: str) -> Dict[str, list]:
    doc = nlp(message)
    return {
        "locations": [ent.text.strip() for ent in doc.ents if ent.label_.lower() in ["gpe", "loc"]],
    }

def parse_natural_date(raw_date: str) -> str:
    parsed = dateparser.parse(raw_date, languages=['id'])
    return parsed.strftime("%Y-%m-%d") if parsed else raw_date

def extract_slots(intent: str, message: str) -> Dict[str, str]:
    slots = {}
    msg = normalize(message)
    ents = extract_entities(message)

    if intent == "book_flight":
        from_match = re.search(FROM_PATTERN, msg)
        to_match = re.search(TO_PATTERN, msg)
        date_match = re.search(DATE_PATTERN, msg)

        if from_match:
            slots["from"] = from_match.group(1).strip()
        elif len(ents["locations"]) > 0:
            slots["from"] = ents["locations"][0]

        if to_match:
            slots["to"] = to_match.group(1).strip()
        elif len(ents["locations"]) > 1:
            slots["to"] = ents["locations"][1]

        if date_match:
            raw_date = date_match.group(0)
            slots["departure_date"] = parse_natural_date(raw_date)

    elif intent == "book_hotel":
        loc_match = re.search(LOC_PATTERN, msg)
        night_match = re.search(NIGHT_PATTERN, msg)
        date_match = re.search(DATE_PATTERN, msg)

        if loc_match:
            slots["location"] = loc_match.group(1).strip()
        elif ents["locations"]:
            slots["location"] = ents["locations"][0]

        if night_match:
            slots["duration_nights"] = night_match.group(1)

        if date_match:
            slots["checkin_date"] = parse_natural_date(date_match.group(0))

    elif intent == "plan_trip":
        dest_match = re.search(LOC_PATTERN, msg)
        if dest_match:
            slots["destination"] = dest_match.group(1).strip()
        elif ents["locations"]:
            slots["destination"] = ents["locations"][0]

    elif intent == "find_attractions":
        loc_match = re.search(LOC_PATTERN, msg)
        if loc_match:
            slots["location"] = loc_match.group(1).strip()
        elif ents["locations"]:
            slots["location"] = ents["locations"][0]

    return slots
