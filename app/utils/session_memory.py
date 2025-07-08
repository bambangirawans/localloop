# app/utils/session_memory.py

import time
from typing import Dict, Optional, Any

_session_cache: Dict[str, Dict[str, Any]] = {}

SESSION_TTL = 60 * 30  # 30 menit

def remember_intent(user_id: str, intent: str, slots: Optional[Dict[str, str]] = None) -> None:
    if user_id not in _session_cache:
        _session_cache[user_id] = {}
    _session_cache[user_id]["last_intent"] = intent
    if slots:
        _session_cache[user_id]["last_slots"] = slots
    _session_cache[user_id]["last_interaction"] = time.time()

def get_last_intent(user_id: str) -> Optional[str]:
    return _session_cache.get(user_id, {}).get("last_intent")

def get_last_slots(user_id: str) -> Dict[str, str]:
    return _session_cache.get(user_id, {}).get("last_slots", {})

def get_last_interaction_time(user_id: str) -> float:
    return _session_cache.get(user_id, {}).get("last_interaction", 0.0)

def clear_session(user_id: str) -> None:
    if user_id in _session_cache:
        _session_cache.pop(user_id)

def update_user_context(user_id: str, context: Dict[str, Any]) -> None:
    if user_id not in _session_cache:
        _session_cache[user_id] = {}
    _session_cache[user_id].update(context)
    _session_cache[user_id]["last_interaction"] = time.time()

def get_user_context(user_id: str) -> Dict[str, Any]:
    return _session_cache.get(user_id, {})

def is_session_expired(user_id: str) -> bool:
    last_time = get_last_interaction_time(user_id)
    return (time.time() - last_time) > SESSION_TTL
    
def get_last_stage(user_id: str) -> Optional[str]:
    return _session_cache.get(user_id, {}).get("last_stage")

def get_last_domain(user_id: str) -> Optional[str]:
    return _session_cache.get(user_id, {}).get("last_domain")

