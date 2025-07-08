#app/domains/marketplace/checkout.py

from typing import Dict, Union
from app.lang_detect import detect_language
from app.utils.external_search import use_tavily, use_serpapi_search
from app.llama_agent import ask_llama

def can_handle(intent: str) -> bool:
    return intent in ["buy_product", "sell_product", "search_deals"]

def handle(intent: str, slots: Dict[str, Union[str, dict]], user_id: str) -> str:
    ref_text = slots.get("product") or slots.get("category") or "produk"
    lang = detect_language(ref_text)

    if intent == "buy_product":
        product = slots.get("product")
        if product:
            query = f"tempat beli {product} murah online" if lang == "id" else f"where to buy {product} online cheap"
            results = use_tavily(query) or use_serpapi_search(query)

            if not results:
                return {
                    "id": f"🙏 Maaf, saya tidak menemukan {product} saat ini.",
                    "en": f"🙏 Sorry, I couldn't find {product} right now.",
                }.get(lang)

            prompt = {
                "id": f"Tampilkan hasil pencarian dan rekomendasikan toko online terbaik untuk membeli {product}:\n\n{results}",
                "en": f"Summarize search results and recommend the best online store to buy {product}:\n\n{results}",
            }.get(lang)

            summary = ask_llama(prompt)
            return {
                "id": f"🛒 Berikut rekomendasi pembelian untuk {product}:\n\n{summary}",
                "en": f"🛒 Here's a recommendation for buying {product}:\n\n{summary}",
            }.get(lang)

        return {
            "id": "🛒 Produk apa yang ingin Anda beli?",
            "en": "🛒 What product would you like to buy?",
        }.get(lang)

    if intent == "sell_product":
        item = slots.get("product")
        if item:
            prompt = {
                "id": f"Buat deskripsi singkat dan menarik untuk menjual produk {item} di marketplace.",
                "en": f"Create a short and compelling description for selling {item} on a marketplace.",
            }.get(lang)
            listing_desc = ask_llama(prompt)

            return {
                "id": f"📤 Barang {item} Anda telah dicantumkan di marketplace dengan deskripsi:\n\n{listing_desc}",
                "en": f"📤 Your item {item} has been listed on the marketplace with the following description:\n\n{listing_desc}",
            }.get(lang)

        return {
            "id": "📤 Barang apa yang ingin Anda jual?",
            "en": "📤 What item would you like to sell?",
        }.get(lang)

    if intent == "search_deals":
        category = slots.get("category")
        if category:
            query = f"promo terbaik untuk {category} minggu ini" if lang == "id" else f"best deals for {category} this week"
            results = use_tavily(query) or use_serpapi_search(query)

            if not results:
                return {
                    "id": f"🙏 Tidak ditemukan promo terbaru untuk kategori {category}.",
                    "en": f"🙏 Couldn't find recent deals for {category}.",
                }.get(lang)

            prompt = {
                "id": f"Ringkas hasil pencarian promo untuk kategori {category}:\n\n{results}",
                "en": f"Summarize search results for deals in category {category}:\n\n{results}",
            }.get(lang)

            summary = ask_llama(prompt)
            return {
                "id": f"🔥 Promo terbaik minggu ini untuk kategori {category}:\n\n{summary}",
                "en": f"🔥 This week's best deals for category {category}:\n\n{summary}",
            }.get(lang)

        return {
            "id": "🔥 Anda ingin melihat promo untuk kategori apa?",
            "en": "🔥 Which category are you interested in for deals?",
        }.get(lang)

    return {
        "id": "❓ Maaf, saya belum mengerti permintaan Anda.",
        "en": "❓ Sorry, I didn't understand your request.",
    }.get(lang, "Sorry, I’m not sure how to proceed.")
