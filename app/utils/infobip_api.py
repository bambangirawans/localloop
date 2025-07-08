# app/utils/infobip_api.py

import os
import json
import requests
from app.utils import user_graph


INFOBIP_API_KEY = os.getenv("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.getenv("INFOBIP_BASE_URL")
INFOBIP_SENDER = os.getenv("INFOBIP_SENDER")


HEADERS = {
    "Authorization": f"App {INFOBIP_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def send_whatsapp_message(to_number: str, text: str):
    url = f"{INFOBIP_BASE_URL}/whatsapp/1/message/text"
    payload = {
        "from": INFOBIP_SENDER,
        "to": to_number,
        "message": {"text": text}
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"error": "Invalid JSON response"}

def receive_whatsapp_webhook(request_data):
    user_id = request_data.get("from")
    text = request_data.get("message", {}).get("text")
    if text:
        user_graph.add_recent_search(user_id, text)
        return True
    return False

def save_feedback(user_id: str, feedback: str, original_prompt: str = None, output: str = None):
    user_graph.add_feedback(user_id, feedback)

    if original_prompt and output:
        os.makedirs("data", exist_ok=True)
        with open("data/feedback_training.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "prompt": original_prompt,
                "completion": output,
                "feedback": feedback,
                "user_id": user_id
            }, ensure_ascii=False) + "\n")

