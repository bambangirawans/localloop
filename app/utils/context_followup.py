# app/utils/context_followup.py

from sentence_transformers import SentenceTransformer, util
from app.utils.session_memory import get_last_intent, get_last_slots


FOLLOWUP_PHRASES = [
    # Bahasa Indonesia
    "dan kemudian?", "terus?", "gimana selanjutnya?", "lalu?", "apa lagi?", "lanjut", "oke, lalu?",
    "baik, terus?", "ok lanjut", "lalu bagaimana?", "selanjutnya?", "terus pesan apa?",
    "bagaimana dengan itu?",

    # English
    "what’s next?", "how about that?", "then?", "what else?", "continue", "what happens next?",
    "okay, then?", "so what now?", "go on", "what did we decide?", "and after that?"
]

embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
FOLLOWUP_EMBEDDINGS = embedding_model.encode(FOLLOWUP_PHRASES, convert_to_tensor=True)

def is_contextual_followup(message: str, user_id: str, threshold: float = 0.70) -> bool:
    message = message.strip().lower()
    if not message:
        return False

    if len(message.split()) <= 4:
        message_embedding = embedding_model.encode(message, convert_to_tensor=True)
        similarities = util.cos_sim(message_embedding, FOLLOWUP_EMBEDDINGS)[0]
        if float(similarities.max()) > threshold:
            return True

    return get_last_intent(user_id) is not None


def get_contextual_prompt(user_id: str, lang: str = "en") -> str:
    last_intent = get_last_intent(user_id)
    last_slots = get_last_slots(user_id)

    if not last_intent:
        return {
            "en": "The user is continuing a previous conversation, but the intent is unclear.",
            "id": "Pengguna melanjutkan percakapan sebelumnya, tetapi maksudnya tidak jelas."
        }.get(lang, "The user is continuing a previous conversation.")

    context = {
        "en": f"Previously, the user wanted to **{last_intent.replace('_', ' ')}**",
        "id": f"Sebelumnya, pengguna ingin **{last_intent.replace('_', ' ')}**"
    }

    if last_slots:
        slot_desc = ", ".join(f"{k}: {v}" for k, v in last_slots.items())
        context["en"] += f" with details: {slot_desc}"
        context["id"] += f" dengan detail: {slot_desc}"

    return context.get(lang, context["en"])
