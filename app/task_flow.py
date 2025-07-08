# app/task_flow.py

from app.intents.intent_classifier import classify_intent

task_flow_stages = {
    "order_food": "order",
    "find_restaurant": "search",
    "recommendation": "search",
    "book_flight": "book",
    "find_hotel": "search",
    "travel_recommendation": "search",
    "buy_product": "cart",
    "search_product": "search",
    "product_recommendation": "search"
}

domain_task_flow = {
    "food": ["search", "menu", "order", "cart", "checkout", "confirm"],
    "travel": ["search", "select", "book", "payment", "confirm"],
    "marketplace": ["search", "compare", "order", "cart", "payment", "confirm"]
}

next_step_prompts = {
    "id": {
        "search": "🔍 Kamu bisa lihat menu atau pilih yang ingin dipesan.",
        "menu": "🍽 Mau pesan sesuatu dari menu ini?",
        "order": "🛒 Lanjutkan dengan melihat keranjang pesanan kamu.",
        "cart": "💳 Siap checkout? Lanjut ke pembayaran ya.",
        "checkout": "✅ Konfirmasi pesanan jika semua sudah sesuai.",
        "select": "🎯 Silakan pilih opsi yang kamu inginkan.",
        "book": "✈️ Ingin lanjutkan pemesanan?",
        "payment": "💳 Lanjutkan ke pembayaran ya.",
        "compare": "📊 Mau bandingkan produk lain?",
        "confirm": "🎉 Semua selesai. Terima kasih sudah menggunakan layanan kami!"
    },
    "en": {
        "search": "🔍 You can now view the menu or choose something to order.",
        "menu": "🍽 Would you like to order something from this menu?",
        "order": "🛒 Next, review your cart before checkout.",
        "cart": "💳 Ready to checkout? Proceed to payment.",
        "checkout": "✅ Confirm your order when everything looks good.",
        "select": "🎯 Please select the option you prefer.",
        "book": "✈️ Want to proceed with the booking?",
        "payment": "💳 Go ahead and make your payment.",
        "compare": "📊 Want to compare other products?",
        "confirm": "🎉 All set. Thanks for using our service!"
    }
}


def get_task_stage(message: str) -> str:
    intent = classify_intent(message)
    return task_flow_stages.get(intent, "search")


def get_next_stage(stage: str, domain: str, lang: str = "en") -> str:
    flow = domain_task_flow.get(domain, [])
    if stage not in flow:
        return ""

    current_index = flow.index(stage)
    next_index = current_index + 1

    if next_index < len(flow):
        next_stage = flow[next_index]
        return next_step_prompts.get(lang, {}).get(next_stage, "")
    else:
        return next_step_prompts.get(lang, {}).get("confirm", "")
