#app/domains/travel/checkout.py

from typing import Dict, Union
from app.lang_detect import detect_language
from app.utils.external_search import use_tavily, use_serpapi_search
from app.llama_agent import ask_llama

def can_handle(intent: str) -> bool:
    return intent in ["book_flight", "book_hotel", "plan_trip","find_attractions"]

def handle(intent: str, slots: Dict[str, Union[str, dict]], user_id: str) -> str:
    lang = detect_language(
        slots.get("destination") or
        slots.get("location") or
        slots.get("to") or
        slots.get("from") or "perjalanan"
    )

    if intent == "book_flight":
        origin = slots.get("from")
        dest = slots.get("to")
        if origin and dest:
            return {
                "id": f"✈️ Baik, saya bantu pesan tiket dari {origin} ke {dest}. Mohon tunggu sebentar...",
                "en": f"✈️ Great! Booking a flight from {origin} to {dest}. Please hold on...",
            }.get(lang, "Booking flight...")
        elif not origin:
            return "📍 Dari kota mana Anda ingin berangkat?" if lang == "id" else "📍 From which city would you like to depart?"
        elif not dest:
            return "📍 Ke mana tujuan penerbangan Anda?" if lang == "id" else "📍 What is your flight destination?"

    if intent == "book_hotel":
        location = slots.get("location")
        if location:
            query = f"hotel terbaik di {location}" if lang == "id" else f"best hotels in {location}"
            results = use_tavily(query) or use_serpapi_search(query)

            if not results:
                return {
                    "id": f"🙏 Maaf, saya tidak menemukan hotel di {location}.",
                    "en": f"🙏 Sorry, I couldn't find hotels in {location}.",
                }.get(lang)

            prompt = {
                "id": f"Berikut hasil pencarian hotel di {location}. Ringkas dan tampilkan rekomendasi terbaik:\n\n{results}",
                "en": f"Here's a hotel search result in {location}. Summarize and highlight top hotel options:\n\n{results}",
            }.get(lang)

            llm_response = ask_llama(prompt)
            return {
                "id": f"🏨 Ini beberapa rekomendasi hotel di {location}:\n\n{llm_response}",
                "en": f"🏨 Here are some hotel recommendations in {location}:\n\n{llm_response}",
            }.get(lang)

        return {
            "id": "🏨 Di mana Anda ingin menginap?",
            "en": "🏨 Where would you like to stay?",
        }.get(lang)

    if intent == "plan_trip":
        destination = slots.get("destination")
        if destination:
            query = f"tempat wisata dan itinerary di {destination}" if lang == "id" else f"tourist attractions and travel itinerary in {destination}"
            results = use_tavily(query) or use_serpapi_search(query)

            if not results:
                return {
                    "id": f"🙏 Maaf, belum ada informasi itinerary untuk {destination}.",
                    "en": f"🙏 Sorry, I couldn't find a travel plan for {destination}.",
                }.get(lang)

            prompt = {
                "id": f"Buat itinerary liburan 3 hari ke {destination} berdasarkan informasi ini:\n\n{results}",
                "en": f"Create a 3-day travel itinerary for {destination} based on this info:\n\n{results}",
            }.get(lang)

            llm_response = ask_llama(prompt)
            return {
                "id": f"🗺️ Berikut itinerary ke {destination} yang bisa Anda ikuti:\n\n{llm_response}",
                "en": f"🗺️ Here's a travel itinerary for {destination} you can follow:\n\n{llm_response}",
            }.get(lang)

        return {
            "id": "🗺️ Ke mana tujuan liburan Anda?",
            "en": "🗺️ What's your travel destination?",
        }.get(lang)
        
    if intent == "find_attractions":
        location = slots.get("location") or slots.get("destination")
        if location:
            query = f"tempat wisata populer di {location}" if lang == "id" else f"top tourist attractions in {location}"
            results = use_tavily(query) or use_serpapi_search(query)

            if not results:
                return {
                    "id": f"🙏 Maaf, saya tidak menemukan tempat wisata di {location}.",
                    "en": f"🙏 Sorry, I couldn't find tourist attractions in {location}.",
                }.get(lang)

            prompt = {
                "id": f"Berikut hasil pencarian tempat wisata di {location}. Ringkas dan tampilkan rekomendasi menarik:\n\n{results}",
                "en": f"Here's a search result for attractions in {location}. Summarize and highlight interesting spots:\n\n{results}",
            }.get(lang)

            llm_response = ask_llama(prompt)
            return {
                "id": f"📸 Ini beberapa tempat wisata yang bisa Anda kunjungi di {location}:\n\n{llm_response}",
                "en": f"📸 Here are some tourist spots you can visit in {location}:\n\n{llm_response}",
            }.get(lang)

        return {
            "id": "📍 Kota mana yang ingin Anda eksplorasi?",
            "en": "📍 Which city would you like to explore?",
        }.get(lang)

    return {
        "id": "❓ Maaf, saya belum yakin dengan permintaan Anda.",
        "en": "❓ Sorry, I’m not sure what you meant.",
    }.get(lang, "Sorry, I’m not sure how to proceed.")
    

    return {
        "id": "❓ Maaf, saya belum yakin dengan permintaan Anda.",
        "en": "❓ Sorry, I’m not sure what you meant.",
    }.get(lang, "Sorry, I’m not sure how to proceed.")
