# app/domains/food/checkout.py

from typing import Dict, Union
from app.llama_agent import ask_llama
from app.lang_detect import detect_language
from app.utils.external_search import use_tavily, use_serpapi_search
from app.utils.order_memory import get_user_orders, clear_user_orders

def can_handle(intent: str) -> bool:
    return intent in [
        "order_food", "find_restaurant", "confirm_order",
        "check_order_status", "payment_info", "cancel_order",
        "delivery_info", "calculate_total", "real_delivery_eta"
    ]

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

def build_order_cards(orders: list, lang: str) -> list:
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
    orders = slots.get("orders", []) or get_user_orders(user_id)
    delivery_time = slots.get("delivery_time", "")
    location = slots.get("location", "")

    sample_ref = orders[0]["item"] if orders else (location or "makanan")
    lang = detect_language(sample_ref)

    if intent == "confirm_order":
        return {
            "text": {
                "id": "✅ Pesanan Anda telah dikonfirmasi!",
                "en": "✅ Your order has been confirmed!"
            }.get(lang),
            "render": {
                "type": "order_confirmation",
                "orders": build_order_cards(orders, lang)
            }
        }

    elif intent == "check_order_status":
        return {
            "text": {
                "id": "⌛ Pesanan Anda sedang diproses dan akan segera dikirim.",
                "en": "⌛ Your order is being prepared and will be delivered soon."
            }.get(lang),
            "render": {
                "type": "order_status",
                "status": "processing"
            }
        }

    elif intent == "cancel_order":
        clear_user_orders(user_id)
        return {
            "text": {
                "id": "⚠️ Pesanan dibatalkan dan histori dihapus.",
                "en": "⚠️ Order has been canceled and history cleared."
            }.get(lang),
            "render": {
                "type": "cancellation"
            }
        }

    elif intent == "payment_info":
        search_result = use_tavily("most used food delivery payment methods in Indonesia") \
                        or use_serpapi_search("best payment options for food delivery Indonesia")

        prompt = f"""
Based on the following web results, what are the top 3 payment methods used for food delivery in Indonesia?

{search_result}

Return only method names (no description), like:
1. Stripe
2. Paypal
3. Credit Card
"""
        methods = ask_llama(prompt)

        return {
            "text": {
                "id": f"💳 Metode pembayaran yang tersedia:\n{methods}",
                "en": f"💳 Available payment methods:\n{methods}"
            }.get(lang),
            "render": {
                "type": "payment_options",
                "methods": [m.strip("1234. ") for m in methods.split("\n") if m.strip()]
            }
        }

    elif intent == "calculate_total":
        if not orders:
            return {
                "text": {
                    "id": "❌ Tidak ada item dalam pesanan.",
                    "en": "❌ No items found in the order."
                }.get(lang),
                "render": None
            }

        item_names = ", ".join([o["item"] for o in orders])
        query = f"price of {item_names} food menu in Indonesia"
        web_result = use_tavily(query) or use_serpapi_search(query)

        prompt = f"""
You are a food ordering assistant. Based on this user order: {orders}
and the following web results:

{web_result}

Estimate the total price in IDR. Use reasonable average prices for each item. Return just the total in this format:

Total: Rp[amount]
"""
        price_info = ask_llama(prompt)

        return {
            "text": {
                "id": f"💰 Estimasi total pembayaran: {price_info}",
                "en": f"💰 Estimated total payment: {price_info}"
            }.get(lang),
            "render": {
                "type": "payment_estimate",
                "orders": build_order_cards(orders, lang),
                "total_price": price_info
            }
        }

    elif intent == "real_delivery_eta":
        if not location:
            return {
                "text": {
                    "id": "📍 Mohon info lokasi untuk estimasi waktu pengiriman.",
                    "en": "📍 Please provide a location for delivery time estimation."
                }.get(lang),
                "render": None
            }

        query = f"estimated food delivery time in {location}"
        web_result = use_tavily(query) or use_serpapi_search(query)

        prompt = f"""
Given the user's location "{location}", estimate realistic food delivery time.
Based on this info:

{web_result}

Respond with a clear ETA in minutes or range. Example: '25–40 minutes'
"""
        eta = ask_llama(prompt)

        return {
            "text": {
                "id": f"🚚 Estimasi waktu antar: {eta}",
                "en": f"🚚 Estimated delivery time: {eta}"
            }.get(lang),
            "render": {
                "type": "delivery_tracking",
                "eta": eta
            }
        }

    elif intent == "delivery_info":
        if location:
            return {
                "text": {
                    "id": f"📍 Pesanan Anda akan dikirim ke: {location}",
                    "en": f"📍 Your order will be delivered to: {location}"
                }.get(lang),
                "render": {
                    "type": "delivery_location",
                    "location": location
                }
            }
        else:
            return {
                "text": {
                    "id": "📍 Mohon sebutkan lokasi pengiriman Anda.",
                    "en": "📍 Please provide your delivery location."
                }.get(lang),
                "render": None
            }

    return {
        "text": {
            "id": "🤖 Maaf, saya tidak mengerti permintaan Anda.",
            "en": "🤖 Sorry, I didn’t understand your request."
        }.get(lang),
        "render": None
    }
