import random
from app.lang_detect import detect_language

# Multilingual examples for fallback
examples = {
    "en": [
        "✈️ Looking for flights? Try: 'Search flights to Bali'.",
        "🏨 Need a hotel? Ask: 'Book hotel in Bandung'.",
        "🗺️ Planning a trip? Try: '3-day itinerary in Yogyakarta'.",
        "🚗 Want transport tips? Ask: 'How to get from Jakarta to Surabaya?'.",
        "🎒 Curious about attractions? Try: 'Things to do in Lombok'."
    ],
    "id": [
        "✈️ Cari penerbangan? Coba: 'Cari tiket pesawat ke Bali'.",
        "🏨 Butuh hotel? Tanyakan: 'Pesan hotel di Bandung'.",
        "🗺️ Rencanakan liburan? Coba: 'Itinerary 3 hari di Yogyakarta'.",
        "🚗 Mau tips transportasi? Tanyakan: 'Cara ke Surabaya dari Jakarta'.",
        "🎒 Penasaran tempat wisata? Coba: 'Hal yang bisa dilakukan di Lombok'."
    ]
}

def fallback(message: str) -> str:
    """Generate fallback travel assistant response based on user's language"""
    lang = detect_language(message)

    intro = {
        "en": "🌍 I'm your travel planner! Ask about flights, hotels, or attractions.\n",
        "id": "🌍 Saya perencana perjalanan Anda! Tanyakan penerbangan, hotel, atau destinasi.\n"
    }.get(lang, "🌍 I'm your travel assistant!\n")

    example = random.choice(examples.get(lang, examples["en"]))
    return f"{intro}{example}"
