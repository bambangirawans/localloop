# app/knowledge_graph.py

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF
from app.utils import user_graph

EX = Namespace("http://example.org/")
PREF = Namespace("http://example.org/pref/")

def update_user_profile(user_id: str, message: str):
    user_uri = URIRef(f"http://example.org/{user_id}")
    user_graph.user_graph.add((user_uri, PREF.recent_search, Literal(message.lower())))

    # Optional: keyword extraction → preferences
    keywords = extract_keywords(message)
    for kw in keywords:
        user_graph.user_graph.add((user_uri, PREF.likes, Literal(kw.lower())))

def build_context_prompt(user_id: str) -> str:
    prefs = user_graph.get_user_preference_tags(user_id)
    searches = user_graph.get_recent_searches(user_id)
    return (
        f"User Preferences: {', '.join(prefs)}\n"
        f"Recent Searches: {', '.join(searches)}"
    )

def extract_keywords(text: str):
    return [w for w in text.lower().split() if len(w) > 3]
