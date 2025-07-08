import random
from app.lang_detect import detect_language

# Example prompts for different languages
examples = {
    "en": [
        "👜 Looking for second-hand items? Try: 'Find used bikes near me'.",
        "📱 Need electronics? Ask: 'Show me affordable smartphones'.",
        "👟 Want fashion deals? Try: 'Latest sneaker deals online'.",
        "🛒 Curious about promotions? Say: 'What's trending in the marketplace?'.",
        "🎁 Need gift ideas? Try: 'Top 5 products under $20'."
    ],
    "id": [
        "👜 Cari barang bekas? Coba: 'Temukan sepeda bekas di dekat saya'.",
        "📱 Butuh elektronik? Tanyakan: 'Tampilkan smartphone terjangkau'.",
        "👟 Ingin diskon fashion? Coba: 'Promo sepatu terbaru online'.",
        "🛒 Cari promo menarik? Katakan: 'Apa yang sedang tren di marketplace?'.",
        "🎁 Butuh ide hadiah? Coba: 'Top 5 produk di bawah 100 ribu'."
    ]
}

def fallback(message: str) -> str:
    """Generate fallback marketplace assistant response based on language"""
    lang = detect_language(message)

    intro = {
        "en": "🛍️ I'm your shopping assistant! Ask me about products, deals, or categories.\n",
        "id": "🛍️ Saya asisten belanja Anda! Tanyakan produk, promo, atau kategori.\n"
    }.get(lang, "🛍️ I'm your marketplace assistant!\n")

    # Fallback to English examples if the language is unsupported
    example = random.choice(examples.get(lang, examples["en"]))
    return f"{intro}{example}"
