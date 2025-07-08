from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, FOAF
import uuid
import os


EX = Namespace("http://example.org/")
PREF = Namespace("http://example.org/pref/")
FB = Namespace("http://example.org/feedback/")

user_graph = Graph()

def init_graph():
    user_graph.bind("ex", EX)
    user_graph.bind("pref", PREF)
    user_graph.bind("fb", FB)

    user = EX["anonymous_user"]
    user_graph.add((user, RDF.type, FOAF.Person))
    user_graph.add((user, FOAF.name, Literal("Budi")))
    user_graph.add((user, PREF.likes, Literal("makanan jepang")))
    user_graph.add((user, PREF.likes, Literal("elektronik")))
    user_graph.add((user, PREF.recent_search, Literal("kamera mirrorless")))
    user_graph.add((user, PREF.recent_search, Literal("promo nasi goreng")))
    user_graph.add((user, PREF.language, Literal("id")))

def _get_user_uri(user_id: str):
    return URIRef(f"http://example.org/{user_id}")


def get_user_preference_tags(user_id: str):
    user_uri = _get_user_uri(user_id)
    query = f"""
    SELECT ?pref WHERE {{
        <{user_uri}> <{PREF.likes}> ?pref .
    }}
    """
    results = user_graph.query(query)
    return [str(row.pref).lower() for row in results]

def get_recent_searches(user_id: str):
    user_uri = _get_user_uri(user_id)
    query = f"""
    SELECT ?search WHERE {{
        <{user_uri}> <{PREF.recent_search}> ?search .
    }}
    """
    results = user_graph.query(query)
    return [str(row.search) for row in results]

def add_user_preference(user_id: str, preference: str):
    user_uri = _get_user_uri(user_id)
    if preference.lower() not in get_user_preference_tags(user_id):
        user_graph.add((user_uri, PREF.likes, Literal(preference.lower())))

def add_recent_search(user_id: str, search_query: str):
    user_uri = _get_user_uri(user_id)
    if search_query.lower() not in get_recent_searches(user_id):
        user_graph.add((user_uri, PREF.recent_search, Literal(search_query.lower())))

def get_user_language(user_id: str) -> str:
    user_uri = _get_user_uri(user_id)
    query = f"""
    SELECT ?lang WHERE {{
        <{user_uri}> <{PREF.language}> ?lang .
    }}
    """
    results = user_graph.query(query)
    langs = [str(row.lang).lower() for row in results]
    return langs[0] if langs else "en"

def set_user_language(user_id: str, lang: str):
    user_uri = _get_user_uri(user_id)
    user_graph.set((user_uri, PREF.language, Literal(lang.lower())))


def store_feedback(node_uri: str, feedback: str):
    subj = URIRef(node_uri)
    feedback_node = FB[str(uuid.uuid4())]
    user_graph.add((feedback_node, RDF.type, FB.Feedback))
    user_graph.add((feedback_node, FB.forNode, subj))
    user_graph.add((feedback_node, FB.comment, Literal(feedback)))
    save_graph_to_ttl()
    print(f"[✅] Stored feedback for {node_uri}")

def add_user_feedback(user_id: str, feedback: str):
    user_uri = _get_user_uri(user_id)
    feedback_node = FB[str(uuid.uuid4())]
    user_graph.add((feedback_node, RDF.type, FB.Feedback))
    user_graph.add((feedback_node, FB.user, user_uri))
    user_graph.add((feedback_node, FB.comment, Literal(feedback)))
    save_graph_to_ttl()
    print(f"[💬] Saved feedback from {user_id}: {feedback}")

def export_feedback_data(path="data/user_feedback.txt"):
    feedbacks = []
    for _, _, o in user_graph.triples((None, FB.comment, None)):
        feedbacks.append(str(o))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in feedbacks)
    print(f"[📤] Exported {len(feedbacks)} feedback entries to {path}")


def save_graph_to_ttl(path="data/user_profile.ttl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    user_graph.serialize(destination=path, format="turtle")
    print(f"[📚] Saved graph to {path}")

def export_graph_rdfxml(path="model/user_graph.rdf"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    user_graph.serialize(destination=path, format="xml")
    print(f"[📤] Exported RDF/XML to {path}")

def export_graph_dot(path="model/user_graph.dot"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("digraph user_graph {\n")
        for s, p, o in user_graph:
            f.write(f'"{s}" -> "{o}" [label="{p}"];\n')
        f.write("}\n")
    print(f"[📤] Exported DOT graph to {path}")
