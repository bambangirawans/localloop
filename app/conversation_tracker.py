# app/conversation_tracker.py

from typing import Dict

CONTEXT = {}

def update_context(user_id: str, key: str, value: str):
    if user_id not in CONTEXT:
        CONTEXT[user_id] = {}
    CONTEXT[user_id][key] = value


def get_context(user_id: str, key: str) -> str:
    return CONTEXT.get(user_id, {}).get(key, "")


def reset_context(user_id: str):
    if user_id in CONTEXT:
        CONTEXT[user_id] = {}


def is_follow_up(user_id: str, message: str) -> bool:
    follow_ups = ["ya", "yes", "ok", "okay", "lanjut", "iya", "mau", "pesan", "tomorrow"]
    return message.strip().lower() in follow_ups
