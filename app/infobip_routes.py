# app/infobip_routes.py

import os
import logging
from flask import Blueprint, request, jsonify, abort
import requests
from app.agent_orchestrator import run_orchestrated_agent
from app.utils.user_graph import add_recent_search, add_user_feedback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

infobip_bp = Blueprint("infobip", __name__)


INFOBIP_API_KEY = os.getenv("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.getenv("INFOBIP_BASE_URL")
INFOBIP_SENDER = os.getenv("INFOBIP_SENDER")

assert INFOBIP_API_KEY, "INFOBIP_API_KEY not set"
assert INFOBIP_BASE_URL, "INFOBIP_BASE_URL not set"
assert INFOBIP_SENDER, "INFOBIP_SENDER not set"

def send_whatsapp_reply(to_number: str, text: str) -> bool:
    url = f"{INFOBIP_BASE_URL}/whatsapp/1/message/text"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": INFOBIP_SENDER,
        "to": to_number,
        "message": {"text": text}
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        logger.error("WhatsApp send error %s: %s", resp.status_code, resp.text)
    return resp.status_code == 200

def send_voice_reply(to_number: str, text: str, language: str = 'en', voice: str = 'Joanna') -> bool:
    url = f"{INFOBIP_BASE_URL}/tts/3/voice"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": INFOBIP_SENDER,
        "to": to_number,
        "text": text,
        "language": language,
        "voice": voice
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        logger.error("Voice send error %s: %s", resp.status_code, resp.text)
    return resp.status_code == 200

@infobip_bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    # You can implement signature validation if needed
    data = request.get_json(force=True)
    logger.info("Incoming WhatsApp payload: %s", data)

    for result in data.get("results", []):
        user_id = result.get("from")
        message_text = result.get("message", {}).get("text", {}).get("body", "").strip()

        if not message_text:
            continue

        if message_text.lower().startswith("feedback:"):
            feedback = message_text[len("feedback:"):].strip()
            add_user_feedback(user_id, feedback)
            send_whatsapp_reply(user_id, "✅ Thanks! Your feedback has been recorded.")
            continue

        add_recent_search(user_id, message_text)
        response = run_orchestrated_agent(message_text, user_id)
        send_whatsapp_reply(user_id, response)

    return jsonify({"status": "processed"}), 200

@infobip_bp.route("/voice", methods=["POST"])
def voice_webhook():
    data = request.get_json(force=True)
    logger.info("Incoming Voice payload: %s", data)

    for result in data.get("results", []):
        user_id = result.get("from")
        speech_body = result.get("speech", {}).get("text", "").strip()

        if speech_body:
            add_recent_search(user_id, speech_body)
            response = run_orchestrated_agent(speech_body, user_id)
            send_voice_reply(user_id, response)

    return jsonify({"status": "processed"}), 200

