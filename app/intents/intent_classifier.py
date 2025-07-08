# app/intents/intent_classifier.py

from sentence_transformers import SentenceTransformer, util
from typing import List, Optional
import torch

intent_labels = [
    "order_food", "find_restaurant", "recommendation",
    "book_flight", "find_hotel", "travel_recommendation",
    "buy_product", "search_product", "product_recommendation"
]

intent_examples = {
    "order_food": [
        "I'd like to order food", "pesan makanan", "I want sushi", "beli makanan",
        "delivery pizza", "mau makan ayam", "order makanan", "mau gofood",
        "pesan gofood", "beli makanan online", "order grabfood", "lagi lapar nih",
        "antar makanan ke rumah", "makanannya apa ya?", "lagi pengen mie"
    ],
    "find_restaurant": [
        "cari restoran", "restaurant near me", "tempat makan enak", "restoran terdekat",
        "find place to eat", "mau makan di luar", "cari tempat makan",
        "tempat makan malam romantis", "restoran yang buka sekarang", "ada restoran enak?",
        "dimana tempat makan enak?", "tempat makan keluarga", "resto enak di jakarta",
        "restoran all you can eat"
    ],
    "recommendation": [
        "makan apa ya?", "recommend me something", "saran makanan", "kasih rekomendasi makanan",
        "any good food?", "what do you recommend?", "kasih ide makan siang",
        "rekomendasi makanan enak", "bingung mau makan apa", "mau yang pedas",
        "ada rekomendasi makan malam?", "suggest makanan simple", "what's good to eat?"
    ],
    "book_flight": [
        "book a flight", "pesan tiket pesawat", "I want to fly", "terbang ke bali",
        "cari penerbangan", "beli tiket pesawat", "flight to Jakarta",
        "booking tiket ke surabaya", "penerbangan murah", "tiket promo pesawat",
        "jadwal pesawat hari ini", "mau ke bandara", "beli tiket pp jakarta bali"
    ],
    "find_hotel": [
        "cari hotel", "hotel murah di bali", "find me a place to stay", "penginapan di ubud",
        "booking hotel", "akomodasi murah", "tempat menginap", "cari homestay",
        "hotel yang dekat pantai", "hotel bintang 5", "budget hotel", "hostel murah",
        "penginapan dekat bandara", "hotel untuk keluarga"
    ],
    "travel_recommendation": [
        "tempat liburan", "where should I go?", "tourist spot", "rekomendasi destinasi",
        "tempat wisata bagus", "liburan kemana ya?", "travel ideas",
        "rekomendasi tempat traveling", "spot wisata populer", "liburan keluarga kemana?",
        "cari tempat healing", "tujuan wisata", "short getaway ideas"
    ],
    "buy_product": [
        "beli hp", "buy phone", "shopping online", "mau beli baju", "pesan laptop",
        "belanja elektronik", "buy shoes", "beli sepatu online", "beli barang di tokopedia",
        "checkout di shopee", "beli barang ini", "beli produk kecantikan", "shopping time",
        "mau order barang ini", "beli mainan anak", "order sepatu nike", "beli earphone bluetooth"
    ],
    "search_product": [
        "cari barang", "search product", "product lookup", "nyari tas online",
        "cari barang elektronik", "search for item", "cari produk diskon",
        "nyari barang murah", "cari hp second", "search gadget", "cari barang di marketplace",
        "apa ada diskon?", "barang promo hari ini", "lihat produk ini"
    ],
    "product_recommendation": [
        "produk bagus", "recommend product", "apa yang terbaik?", "rekomendasi gadget",
        "best product", "what should I buy?", "produk terbaik apa ya?",
        "barang recommended", "apa hp terbaik 2025?", "rekomendasi laptop untuk kerja",
        "minta saran beli barang", "produk terbaik di shopee", "barang yang lagi tren",
        "apa yang paling worth it?", "best value product"
    ]
}

intent_domains = {
    "order_food": "food",
    "find_restaurant": "food",
    "recommendation": "food",
    "book_flight": "travel",
    "find_hotel": "travel",
    "travel_recommendation": "travel",
    "buy_product": "marketplace",
    "search_product": "marketplace",
    "product_recommendation": "marketplace"
}

domain_keywords = {
    "food": [
        "makan", "makanan", "pesan makanan", "restoran", "tempat makan", "antar makanan", "kuliner",
        "menu", "lapar", "sarapan", "makan siang", "makan malam", "warung",
        "food", "eat", "hungry", "order food", "delivery", "restaurant", "dinner", "lunch", "breakfast",
        "meal", "place to eat"
    ],
    "travel": [
        "hotel", "penginapan", "liburan", "perjalanan", "pesawat", "tiket", "terbang", "bandara", "check in",
        "tempat wisata", "akomodasi",
        "flight", "vacation", "trip", "travel", "airport", "tourist", "destination", "stay", "book flight", "tour", "booking"
    ],
    "marketplace": [
        "beli", "barang", "produk", "belanja", "diskon", "promo", "harga", "jual", "pesan barang", "transaksi",
        "marketplace", "cari produk",
        "buy", "shop", "product", "item", "sell", "order", "discount", "price", "purchase", "online shopping",
        "deal", "sale", "ecommerce"
    ]
}

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

label_vectors = {
    intent: model.encode(examples, convert_to_tensor=True)
    for intent, examples in intent_examples.items()
}

def classify_intent(message: str, threshold: float = 0.55, mode: str = "text") -> Optional[str]:
    query_vec = model.encode(message, convert_to_tensor=True)
    best_score = 0.0
    selected_intent = None

    msg_lower = message.lower()
    domain_score = {domain: 0 for domain in domain_keywords}
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in msg_lower:
                domain_score[domain] += 1

    dominant_domain = max(domain_score, key=domain_score.get)
    domain_boost = 0.05 if domain_score[dominant_domain] > 0 else 0.0

    for intent, vectors in label_vectors.items():
        cos_scores = util.cos_sim(query_vec, vectors)
        score = torch.max(cos_scores).item()

        if intent_domains[intent] == dominant_domain:
            score += domain_boost

        if score > best_score:
            best_score = score
            selected_intent = intent
        try:
            threshold = float(threshold)
        except (ValueError, TypeError):
            threshold = 0.55
    return selected_intent if best_score > threshold else None

