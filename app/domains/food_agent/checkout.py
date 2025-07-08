# app/domains/food/checkout.py

from typing import Dict, Union
from app.lang_detect import detect_language
from app.utils.external_search import use_tavily, use_serpapi_search
from app.llama_agent import ask_llama

def can_handle(intent: str) -> bool:
    return intent in ["order_food", "find_restaurant"]

def format_order_list(orders: list, lang: str) -> str:
    if not orders:
        return ""
    phrases = []
    for order in orders:
        qty = order.get("quantity", "1")
        item = order.get("item", "makanan" if lang == "id" else "food")
        qty = str(qty).strip()
        phrase = f"{qty} {item}" if qty != "1" else item
        phrases.append(phrase)

    if len(phrases) > 1:
        connector = " dan " if lang == "id" else " and "
        return f"{', '.join(phrases[:-1])}{connector}{phrases[-1]}"
    return phrases[0]

def format_delivery_time(raw_time: str, lang: str) -> str:
    if not raw_time:
        return ""
    try:
        parts = raw_time.split()
        time_part = parts[0]
        period = parts[1] if len(parts) > 1 else ""
        hour, minute = time_part.split(":") if ":" in time_part else (time_part, "00")
        if lang == "id":
            return f"pukul {hour}.{minute} {period}".strip()
        return f"{hour}:{minute} {period.upper()}".strip()
    except:
        return raw_time

def build_order_cards(orders: list ,lang: str) -> list:
    cards = []
    for order in orders:
        item_name = order.get("item", "makanan" if lang == "id" else "food")
        quantity = order.get("quantity", "1")
        image_url = order.get("image_url")

        card = {
            "title": item_name.title(),
            "subtitle": f"{quantity} pcs",
        }

      
        if image_url:
            card["image"] = image_url
        else:
            card["icon"] = "🍽️"

        cards.append(card)

    return cards

def handle(intent: str, slots: Dict[str, Union[str, list]], user_id: str) -> Union[str, Dict[str, object]]:
    orders = slots.get("orders", [])
    delivery_time = slots.get("delivery_time", "")
    location = slots.get("location", "")

    sample_ref = orders[0]["item"] if orders else (location or "makanan")
    lang = detect_language(sample_ref)

    if intent == "order_food":
        order_text = format_order_list(orders, lang)
        time_text = format_delivery_time(delivery_time, lang)
        location_text = location or ("mana lokasi antarnya?" if lang == "id" else "your delivery location?")

        if lang == "id":
            text = f"🍽️ Baik, saya bantu pesan {order_text}."
            if delivery_time:
                text += f" Akan diantar {time_text}."
            if location:
                text += f" Lokasi antar: {location}."
            else:
                text += f" Boleh tahu {location_text}?"
            text += " Konfirmasi ya jika sudah benar. ✅"
        else:
            text = f"🍽️ Sure, I’ll order {order_text} for you."
            if delivery_time:
                text += f" It will be delivered around {time_text}."
            if location:
                text += f" Delivery to: {location}."
            else:
                text += f" Could you let me know {location_text}?"
            text += " Please confirm. ✅"

        return {
            "text": text,
            "render": {
                "type": "order_summary",
                "orders": build_order_cards(orders),
                "delivery_time": time_text,
                "location": location,
                "confirm_button": True
            }
        }

    if intent == "find_restaurant":
        search_location = location or ("dekat sini" if lang == "id" else "nearby")
        query = f"restoran enak di {search_location}" if lang == "id" else f"good restaurants in {search_location}"
        external_results = use_tavily(query) or use_serpapi_search(query)

        if not external_results:
            return {
                "text": {
                    "id": f"🙏 Maaf, saya tidak menemukan restoran di {search_location}.",
                    "en": f"🙏 Sorry, I couldn't find any restaurants in {search_location}.",
                }.get(lang),
                "render": None
            }

        context = f"Hasil pencarian restoran di {search_location}:\n{external_results}"
        prompt = {
            "id": f"Tolong buatkan ringkasan rekomendasi restoran menarik di {search_location} berdasarkan hasil ini.\n\n{context}",
            "en": f"Please summarize and recommend interesting restaurants in {search_location} based on this info.\n\n{context}"
        }.get(lang, context)

        final_response = ask_llama(prompt)

        return {
            "text": {
                "id": f"✨ Ini rekomendasi untukmu:\n\n{final_response}",
                "en": f"✨ Here’s a recommendation for you:\n\n{final_response}",
            }.get(lang),
            "render": {
                "type": "restaurant_recommendation",
                "location": search_location,
                "raw_results": external_results,
                "summary": final_response
            }
        }

    return {
        "text": {
            "id": "❓ Saya tidak yakin dengan permintaan Anda.",
            "en": "❓ I’m not sure how to proceed with your request.",
        }.get(lang),
        "render": None
    }
