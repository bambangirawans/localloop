# app/main.py

import os
import secrets
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask import redirect, session, url_for
from huggingface_hub import login
from app.llama_agent import ask_llama, MODEL_NAME
from app.utils.user_graph import user_graph, add_recent_search, store_feedback, get_user_preference_tags, get_recent_searches
from app.agent_orchestrator import run_orchestrated_agent
from app.voice.voice_handler import transcribe_audio

load_dotenv()
hf_token = os.getenv("HUGGINGFACE_TOKEN", "").strip()
if hf_token:
    login(token=hf_token)
    
    
def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    from app.utils import init_graph
    init_graph()

    from app.infobip_routes import infobip_bp
    app.register_blueprint(infobip_bp)
    
    from app.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def index(path):
        return render_template("index.html")
    

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json or {}
        message = data.get("message")
        user_id = session.get("phone", "anonymous_user")
        mode = data.get("mode", "text")  # default mode = text

        if not message:
            return jsonify({"error": "No message provided"}), 400

        add_recent_search(user_id, message)
        response = run_orchestrated_agent(message, user_id=user_id, mode=mode)
        return jsonify({"response": response})


    @app.route("/user/preferences", methods=["GET"])
    def get_user_preferences():
        user_id = session.get("phone", "anonymous_user")
        prefs = get_user_preference_tags(user_id)
        return jsonify({"preferences": prefs})


    @app.route("/user/searches", methods=["GET"])
    def get_user_searches():
        user_id = session.get("phone", "anonymous_user")
        searches = get_recent_searches(user_id)
        return jsonify({"recent_searches": searches})

    @app.route("/save_graph", methods=["GET"])
    def save_graph():
        user_graph.export_graph("data/user_profile.ttl")
        return jsonify({"status": "graph saved"})

    @app.route("/status", methods=["GET"])
    def status():
        size = len(user_graph) if user_graph else 0
        return jsonify({
            "message": "LocalLoop AI Agent running",
            "model": MODEL_NAME,
            "profile_graph_triples": size,
        })

    @app.route("/graph", methods=["GET"])
    def view_graph():
        if "phone" not in session:
            return redirect(url_for("auth_bp.login"))  # redirect ke halaman login
        from scripts.visualize_graph import visualize_graph
        visualize_graph("static/graph/graph.html")
        return render_template("iframe_graph.html")

    @app.route("/fraud-check", methods=["POST"])
    def check_fraud():
        data = request.json or {}
        result = predict_fraud(data)
        return jsonify(result)

    @app.route("/voice", methods=["POST"])
    def voice_input():
        audio = request.files.get("audio")
        user_id = session.get("phone", "anonymous_user")

        if not audio:
            return jsonify({"error": "No audio provided"}), 400

        transcription = transcribe_audio(audio)
        if not transcription:
            return jsonify({"transcription": "", "response": "❌ Failed to recognize the voice."})

        response = run_orchestrated_agent(transcription, user_id=user_id, mode="voice")
        return jsonify({"transcription": transcription, "response": response})


    @app.route("/feedback", methods=["POST"])
    def capture_feedback():
        data = request.json
        node = data.get("node")
        feedback = data.get("feedback")
        store_feedback(node, feedback)
        return jsonify({"status": "received"})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
