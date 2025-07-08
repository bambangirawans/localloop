import random
from app.lang_detect import detect_language

# Suggestions for fallback responses by language
suggestions = {
    "en": [
        "🍣 Looking for sushi places nearby? Try asking: 'Find sushi near me'.",
        "🍛 Want to order nasi padang? You can say: 'Order nasi padang for delivery'.",
        "🥢 Craving Asian food? Try: 'Top ramen spots around here'.",
        "🍕 Hungry for pizza? Just ask: 'Pizza delivery in my area'.",
        "🍴 Curious about popular dishes? Try: 'Best Indonesian restaurants in Jakarta'."
    ],
    "id": [
        "🍣 Cari restoran sushi terdekat? Coba: 'Temukan sushi dekat sini'.",
        "🍛 Ingin pesan nasi padang? Katakan: 'Pesan nasi padang untuk antar'.",
        "🥢 Ngidam mie ramen? Tanyakan: 'Tempat ramen terbaik di sekitar sini'.",
        "🍕 Lapar pizza? Coba: 'Pesan pizza area saya'.",
        "🍴 Mau tahu makanan populer? Coba: 'Restoran Indonesia terbaik di Jakarta'."
    ]
}

def fallback(message: str) -> str:
    """Fallback suggestion for food queries if LLM fails to respond confidently"""
    lang = detect_language(message)

    # Intro message per language
    intro = {
        "en": "🍽️ I'm your food assistant! Ask about menus, restaurants, or delivery.\n",
        "id": "🍽️ Saya asisten makanan Anda! Tanyakan menu, restoran, atau layanan antar.\n"
    }.get(lang, "🍽️ I'm your food assistant!\n")

    example = random.choice(suggestions.get(lang, suggestions["en"]))
    return f"{intro}{example}"
