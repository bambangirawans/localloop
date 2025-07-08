#app/utils/domain_detector.py

import torch
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator
from app.intents.intent_classifier import classify_intent
from app.lang_detect import detect_language

translator = Translator()
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

DOMAIN_CANDIDATES = {
    "food": [
        # Indonesian (umum + informal + kuliner)
        "makan", "mau makan", "lagi laper", "lapar", "pesan makanan", "beli makan", "delivery", "pesan makan siang",
        "gofood", "grabfood", "shopeefood", "antar makanan", "restoran", "resto", "rumah makan",
        "cari restoran", "tempat makan", "warteg", "cafe", "kafe", "tempat nongkrong", "kulineran", "nongki",
        "menu makanan", "daftar menu", "rekomendasi makanan", "makanan enak", "makanan lokal", "kuliner lokal", 
        "kuliner indonesia", "masakan khas", "masakan tradisional", "masakan padang", "masakan jawa", "masakan sunda",
        "makan siang", "makan malam", "sarapan", "ngemil", "camilan", "minum kopi", "jajan", "buka puasa",
        "nasi goreng", "nasi padang", "ayam geprek", "sate", "bakso", "mie ayam", "martabak", "burger", "pizza", "ramen", "sushi",
        "snack box", "katering", "hidangan utama", "makanan cepat saji", "cemilan sehat",

        # English / Global
        "order food", "i'm hungry", "food delivery", "takeaway", "dine in", "where to eat", "find restaurant",
        "best food near me", "local food", "street food", "indonesian food", "chinese food", "thai food",
        "korean food", "western food", "asian food", "spicy food", "sweet food", "halal food", "vegetarian food",
        "vegan food", "desserts", "snacks", "grab a bite", "lunch place", "dinner ideas", "breakfast spot",
        "coffee shop", "restaurant recommendations", "food near me", "book a table", "table for two",
        "what’s on the menu", "popular dishes", "cheap food", "healthy food", "fast food", "brunch", "buffet",
        "recommend me food", "food app", "reorder", "my favorite dish"
    ],

    "travel": [
        # Indonesian
        "liburan", "jalan-jalan", "traveling", "wisata", "berwisata", "destinasi wisata", "trip ke bali", "trip ke luar negeri",
        "cari destinasi", "paket liburan", "paket wisata", "booking hotel", "pesan hotel", "cari hotel",
        "akomodasi", "penginapan", "villa", "resort", "homestay", "hotel murah", "staycation", "pengalaman menginap",
        "tiket pesawat", "penerbangan", "pesan tiket", "tiket murah", "cari penerbangan", "bandara", "jadwal pesawat",
        "itinerary", "rencana perjalanan", "travel planner", "traveloka", "tiketcom", "jalan2", "backpacker", "naik pesawat", 
        "transit", "visa", "paspor", "bagasi", "check in", "boarding", "koper", "booking ulang", "refund tiket",

        # English
        "travel", "vacation", "trip", "holiday", "tour", "book a trip", "plan vacation", "where to travel", "travel destination",
        "find hotel", "book hotel", "accommodation", "cheap flights", "airline tickets", "plane ticket", "one-way flight",
        "round trip", "return ticket", "flight deals", "book flight", "flight booking", "explore the world",
        "best places to visit", "travel guide", "city tour", "beach holiday", "mountain trip", "island getaway",
        "visa application", "passport renewal", "travel insurance", "baggage rules", "flight delay", "travel agency",
        "airport transfer", "road trip", "car rental", "train ticket", "europe trip", "asia tour", "honeymoon trip",
        "flight schedule", "cancel flight", "budget travel", "luxury travel", "international trip", "local travel"
    ],

    "marketplace": [
        # Indonesian
        "belanja", "belanja online", "shopping", "beli produk", "beli barang", "beli online", "cari barang",
        "order barang", "toko online", "online shop", "lapak", "e-commerce", "marketplace", "katalog produk",
        "promo", "diskon", "harga murah", "barang murah", "produk murah", "flash sale", "daily deals", "grosir",
        "jual barang", "jual produk", "buka lapak", "lapak digital", "tokopedia", "shopee", "lazada", "bukalapak",
        "barang elektronik", "alat dapur", "kebutuhan rumah", "produk fashion", "pakaian", "sepatu", "tas",
        "smartphone", "gadget", "aksesoris", "hp murah", "beli laptop", "tablet", "baju anak", "popok bayi",
        "pakaian wanita", "jam tangan", "elektronik rumah tangga",

        # English
        "buy item", "buy products", "shop online", "online store", "add to cart", "checkout", "track order",
        "shopping deals", "cheap products", "discounted items", "buy electronics", "tech gadgets", "fashion items",
        "clothes shopping", "buy shoes", "smart devices", "order status", "return product", "refund request",
        "promo code", "wishlist", "shopping app", "online catalog", "compare prices", "product review", 
        "customer rating", "delivery time", "free shipping", "cash on delivery", "ecommerce site", "search product",
        "order now", "buy now", "top seller", "best deal", "hot item", "limited stock", "pre-order",
        "new arrival", "shop by category", "filter product", "find laptop", "home appliances", "kitchen tools"
    ],

    "general": [
        # Bahasa + English campur
        "hello", "hi", "halo", "hey", "apa kabar", "selamat pagi", "selamat malam", "start", "mulai", "bantuan", "help", "tolong",
        "login", "logout", "masuk akun", "daftar", "registrasi", "akun", "profil", "ganti password", "lupa password", "reset password",
        "info akun", "settings", "pengaturan", "preferensi", "ubah bahasa", "ubah tema", "dark mode", "language settings",
        "what can you do", "who are you", "assistant", "bot", "ai agent", "chatbot", "bisa bantu apa", "fitur kamu apa aja",
        "home", "beranda", "kembali", "exit", "restart", "cancel", "stop", "lanjut", "selesai", "oke", "ya", "tidak",
        "faq", "panduan", "tutorial", "cara pakai", "bantuan teknis", "kontak admin", "hubungi kami",
        "feedback", "kritik saran", "lapor masalah", "rate app", "review", "report issue",
        "privacy", "terms", "syarat dan ketentuan", "kebijakan privasi", "graph", "profil pengguna", "activity log"
    ]
}

PHRASE_TO_DOMAIN = {}
ALL_PHRASES = []
for domain, phrases in DOMAIN_CANDIDATES.items():
    for phrase in phrases:
        PHRASE_TO_DOMAIN[phrase] = domain
        ALL_PHRASES.append(phrase)

ALL_PHRASE_EMBEDDINGS = embedding_model.encode(ALL_PHRASES, convert_to_tensor=True)

DOMAIN_EMBEDDINGS = {
    domain: torch.mean(embedding_model.encode(phrases, convert_to_tensor=True), dim=0)
    for domain, phrases in DOMAIN_CANDIDATES.items()
}

def normalize_input(text: str, lang: str) -> str:
    if lang not in ["id", "en"]:
        try:
            return translator.translate(text, dest="id").text
        except Exception as e:
            print(f"[Translation] ⚠️ {e}")
    return text

def detect_domain(message: str, threshold: float = 0.6, top_k: int = 3, debug: bool = False) -> str:
    lang = detect_language(message)
    normalized_msg = normalize_input(message, lang).lower()

    for domain, keywords in DOMAIN_CANDIDATES.items():
        if any(kw in normalized_msg for kw in keywords):
            return domain

    input_vec = embedding_model.encode(normalized_msg, convert_to_tensor=True)
    cos_scores = util.cos_sim(input_vec, ALL_PHRASE_EMBEDDINGS)[0]
    top_results = torch.topk(cos_scores, k=top_k)

    best_domain = None
    max_score = 0.0
    for idx, score in zip(top_results.indices, top_results.values):
        phrase = ALL_PHRASES[idx]
        domain = PHRASE_TO_DOMAIN[phrase]
        if score.item() > max_score:
            max_score = score.item()
            best_domain = domain

    if max_score >= threshold:
        return best_domain

    guessed_intent = classify_intent(normalized_msg)
    fallback_map = {
        "order_food": "food", "find_restaurant": "food",
        "book_hotel": "travel", "book_flight": "travel",
        "buy_item": "marketplace", "search_product": "marketplace"
    }

    if guessed_intent:
        domain = fallback_map.get(guessed_intent, "general")
        return domain

    return "general"
