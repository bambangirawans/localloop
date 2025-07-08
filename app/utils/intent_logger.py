# app/utils/intent_logger.py

from rdflib import Namespace, URIRef, Literal
from app.utils.user_graph import user_graph
import uuid
import datetime

LOG = Namespace("http://example.org/log/")

user_graph.bind("log", LOG)


def log_intent_action(user_id: str, domain: str, intent: str, slots: dict):
    now = datetime.datetime.now().isoformat()
    event_id = str(uuid.uuid4())
    event_uri = URIRef(f"http://example.org/log/{event_id}")
    user_uri = URIRef(f"http://example.org/{user_id}")

    user_graph.add((event_uri, LOG.timestamp, Literal(now)))
    user_graph.add((event_uri, LOG.user, user_uri))
    user_graph.add((event_uri, LOG.domain, Literal(domain)))
    user_graph.add((event_uri, LOG.intent, Literal(intent)))

    for key, value in slots.items():
        user_graph.add((event_uri, LOG[key], Literal(str(value))))

    return event_uri


def export_intent_logs(path="data/intent_logs.ttl"):
    user_graph.serialize(destination=path, format="turtle")
