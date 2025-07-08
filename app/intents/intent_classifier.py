from sentence_transformers import SentenceTransformer, util
from typing import List, Optional
import torch

intent_labels = [
    "order_food", "find_restaurant", "recommendation",
    "book_flight", "find_hotel", "travel_recommendation",
    "buy_product", "search_product", "product_recommendation",
    "payment_info", "calculate_total", "real_delivery_eta",
    "cancel_order", "delivery_info"
]

intent_examples = {
    "order_food": [
        "Saya ingin pesan makanan", "I'd like to order food", "Saya mau sushi", "I want sushi",
        "Pesan makanan online", "Order food delivery", "Saya lapar", "I'm hungry",
        "Bisa gofood?", "Order makanan lewat gofood", "Delivery makanan", "Order makanan sekarang"
    ],
    "find_restaurant": [
        "Cari restoran enak", "Find a good restaurant", "Restoran dekat sini", "Restaurant near me",
        "Tempat makan malam", "Dinner place", "Tempat makan keluarga", "Family dining place",
        "Ada restoran romantis?", "Romantic restaurant nearby"
    ],
    "recommendation": [
        "Rekomendasi makanan", "Food recommendation", "Saya bingung mau makan apa", "I don't know what to eat",
        "Makanan enak apa ya?", "Any good food?", "Mau yang pedas", "I want something spicy"
    ],
    "payment_info": [
        "Bisa bayar pakai apa?", "What payment methods are available?", "Ada pembayaran via QRIS?", "Can I use QRIS?",
        "Metode pembayaran", "Payment options", "Apakah GoPay diterima?", "Is GoPay accepted?"
    ],
    "calculate_total": [
        "Berapa totalnya?", "How much is the total?", "Total semua berapa?", "What's the full price?",
        "Estimasi harga pesanan", "Order cost estimate", "Harga total makanan", "Total food price"
    ],
    "real_delivery_eta": [
        "Kapan sampai?", "When will it arrive?", "Estimasi waktu pengiriman", "Estimated delivery time",
        "Berapa menit makanan sampai?", "How long for delivery?", "Lama pengiriman", "Delivery duration"
    ],
    "cancel_order": [
        "Batalkan pesanan", "Cancel my order", "Saya gak jadi pesan", "I changed my mind",
        "Reset pesanan", "Remove my order", "Hapus pesanan", "Delete my order"
    ],
    "delivery_info": [
        "Alamat pengiriman saya", "My delivery address", "Dikirim ke mana?", "Where is it being sent?",
        "Lokasi saya sekarang", "My current location", "Antar ke alamat ini", "Deliver to this address"
    ],
    "book_flight": [
        "Pesan tiket pesawat", "Book a flight", "Saya ingin ke Bali", "I want to go to Bali",
        "Cari penerbangan murah", "Find a cheap flight", "Tiket ke Jakarta", "Flight to Jakarta"
    ],
    "find_hotel": [
        "Cari hotel", "Find hotel", "Hotel murah di Bandung", "Cheap hotel in Bandung",
        "Akomodasi dekat pantai", "Accommodation near beach", "Booking penginapan", "Book a place to stay"
    ],
    "travel_recommendation": [
        "Rekomendasi tempat liburan", "Vacation recommendation", "Tempat wisata terbaik", "Best tourist destinations",
        "Liburan keluarga kemana?", "Where should we go for a family trip?", "Spot healing", "Nice relaxing spot"
    ],
    "buy_product": [
        "Saya mau beli barang", "I want to buy a product", "Beli HP baru", "Buy new phone",
        "Belanja online", "Online shopping", "Order sepatu", "Order shoes"
    ],
    "search_product": [
        "Cari produk murah", "Search for cheap product", "Nyari barang promo", "Looking for deals",
        "Cari barang elektronik", "Search for electronics", "Lihat produk ini", "Show me this product"
    ],
    "product_recommendation": [
        "Rekomendasi produk terbaik", "Best product recommendation", "Apa yang paling worth it?", "What’s the best value?",
        "Barang yang bagus apa ya?", "Any good item?", "Saran beli gadget", "Recommend a gadget"
    ]
}

intent_domains = {
    "order_food": "food",
    "find_restaurant": "food",
    "recommendation": "food",
    "payment_info": "food",
    "calculate_total": "food",
    "real_delivery_eta": "food",
    "cancel_order": "food",
    "delivery_info": "food",
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
        "meal", "place to eat", "bayar", "qris", "gopay", "ovo", "total", "alamat", "waktu pengiriman", "batal", "cancel"
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

    return selected_intent if best_score > threshold else None
