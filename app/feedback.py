
import json
import os

FEEDBACK_FILE = "data/feedback.json"

def save_feedback(user_id: str, message: str, rating: int, comment: str = ""):
    feedback = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            feedback = json.load(f)
    feedback.append({
        "user_id": user_id,
        "message": message,
        "rating": rating,
        "comment": comment
    })
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
