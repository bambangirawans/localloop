# app/utils/order_memory.py

from typing import List, Dict


ORDER_HISTORY: Dict[str, List[Dict[str, str]]] = {}


def add_order(user_id: str, item: str, quantity: int = 1):

    if user_id not in ORDER_HISTORY:
        ORDER_HISTORY[user_id] = []

    ORDER_HISTORY[user_id].append({
        "item": item,
        "quantity": quantity
    })


def get_user_orders(user_id: str) -> List[Dict[str, str]]:
    return ORDER_HISTORY.get(user_id, [])


def clear_user_orders(user_id: str):

    if user_id in ORDER_HISTORY:
        del ORDER_HISTORY[user_id]


def has_order(user_id: str) -> bool:

    return user_id in ORDER_HISTORY and len(ORDER_HISTORY[user_id]) > 0
