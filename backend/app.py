# backend/app.py

import os
import random
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from redis import Redis
from team_logic import make_teams

# Only load .env in development
if os.getenv("FLASK_ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv()

# ==== STATIC SETUP ====
# Compute path to frontend/dist so Flask can serve the Vue build
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "static")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIST,
    static_url_path="/"
)

# ==== CORS & REDIS ====
# ==== CORS & REDIS ====
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app.logger.info(f"Using REDIS_URL: {redis_url}")
redis_client = Redis.from_url(redis_url, decode_responses=True)
# ==== UTILITIES ====
def generate_session_id():
    """Return a random 6‑digit session ID."""
    return str(random.randint(100000, 999999))

# ==== HEALTH CHECK ====
@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

# ==== SESSION CREATION ====
@app.route("/api/session", methods=["POST"])
def create_session():
    sid = generate_session_id()
    app.logger.info(f"Creating session: {sid}")
    session_obj = {
        "session_id": sid,
        "users": [],
        "settings": {
            "anonymous_mode": False,
            "show_teams_to_users": True,
            "team_size": 4,
            "team_approach": "homogeni",
            "characteristics": [
                "tech_skills", "comm_skills",
                "creative_skills", "leadership_skills",
                "pressure_handling", "team_satisfaction",
                "flexibility", "leadership_frequency",
                "idea_frequency", "self_learning_readiness"
            ],
            "similarity_threshold": 50
        }
    }
    redis_client.set(sid, json.dumps(session_obj))
    return jsonify({"session_id": sid}), 201

# ==== SURVEY SUBMISSION ====
@app.route("/api/session/<sid>/survey", methods=["POST"])
def submit_survey(sid):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404

    sess     = json.loads(stored)
    settings = sess.get("settings", {})

    # Validate required fields
    required = [
        "tech_skills", "comm_skills", "creative_skills", "leadership_skills",
        "preferred_role", "pressure_handling", "team_satisfaction", "flexibility",
        "leadership_frequency", "idea_frequency", "self_learning_readiness",
        "conflict_management"
    ]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Always assign a unique user id if one was not provided
    idx = len(sess["users"]) + 1
    data.setdefault("id", f"user_{idx}")

    # In anonymous mode also replace the provided name
    if settings.get("anonymous_mode"):
        data["name"] = f"User {idx}"

    sess["users"].append(data)
    redis_client.set(sid, json.dumps(sess))
    return jsonify({"status": "ok", "user_id": data.get("id")}), 200

# ==== GET SURVEYS ====
@app.route("/api/session/<sid>/surveys", methods=["GET"])
def get_surveys(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    users = json.loads(stored).get("users", [])
    return jsonify(users), 200

# ==== UPDATE SETTINGS ====
@app.route("/api/session/<sid>/settings", methods=["POST"])
def update_settings(sid):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404

    sess = json.loads(stored)
    sess.setdefault("settings", {}).update(data)
    redis_client.set(sid, json.dumps(sess))
    return jsonify({"status": "ok"}), 200

# ==== GET SETTINGS ====
@app.route("/api/session/<sid>/settings", methods=["GET"])
def get_settings(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    settings = json.loads(stored).get("settings", {})
    return jsonify(settings), 200

# ==== GENERATE TEAMS ====
@app.route("/api/session/<sid>/teams", methods=["POST"])
def generate_teams_endpoint(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404

    sess    = json.loads(stored)
    users   = sess.get("users", [])
    payload = request.get_json(silent=True) or {}
    settings = payload.get("settings", sess.get("settings", {}))

    if len(users) < 2:
        return jsonify({"error": "Need at least 2 users to form teams"}), 400

    df = pd.DataFrame(users)
    teams = make_teams(
        df,
        settings["team_size"],
        settings["team_approach"],
        settings["characteristics"],
        settings["similarity_threshold"]
    )

    # Persist teams
    sess["teams"] = teams
    redis_client.set(sid, json.dumps(sess))

    # Format for response
    formatted = []
    for team in teams:
        members = []
        for m in team["members"]:
            orig = next(
                (u for u in users
                 if all(u.get(k) == m.get(k) for k in m.keys() if k not in ("id", "name"))),
                {}
            )
            member = {
                "id":   orig.get("id", m.get("id")),
                "name": orig.get("name", m.get("name")),
                **m
            }
            members.append(member)
        formatted.append({"members": members, "metrics": team["metrics"]})

    return jsonify({"teams": formatted}), 200

# ==== GET TEAMS ====
@app.route("/api/session/<sid>/teams", methods=["GET"])
def get_teams(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404

    sess     = json.loads(stored)
    teams    = sess.get("teams", [])
    settings = sess.get("settings", {})

    formatted = []
    for team in teams:
        members = []
        for m in team["members"]:
            member = m.copy()
            if settings.get("anonymous_mode"):
                idx = member.get("id", "").split("_")[-1]
                member["name"] = f"User {idx}"
            members.append(member)
        formatted.append({"members": members, "metrics": team["metrics"]})

    return jsonify({"teams": formatted}), 200

# ==== SPA CATCH‑ALL ====
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    # If a real file in dist is requested, serve it; otherwise serve index.html
    full_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(full_path):
        return app.send_static_file(path)
    return app.send_static_file("index.html")

# ==== RUN ====
if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = (os.getenv("FLASK_ENV") == "development")
    app.logger.info(f"Starting Flask on 0.0.0.0:{port}, debug={debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)
