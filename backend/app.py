# backend/app.py

import os
import random
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from redis import Redis
from dotenv import load_dotenv
from team_logic import make_teams

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(redis_url, decode_responses=True)

def generate_session_id():
    return str(random.randint(100000, 999999))

@app.route("/api/session", methods=["POST"])
def create_session():
    sid = generate_session_id()
    redis_client.set(sid, json.dumps({
        "session_id": sid, 
        "users": [],
        "settings": {
            "anonymous_mode": False,
            "show_teams_to_users": True,
            "team_size": 4,
            "team_approach": "homogeni",
            "characteristics": ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"],
            "similarity_threshold": 50
        }
    }))
    return jsonify({"session_id": sid}), 201

@app.route("/api/session/<sid>/survey", methods=["POST"])
def submit_survey(sid):
    data = request.json
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    sess = json.loads(stored)
    sess["users"].append(data)
    redis_client.set(sid, json.dumps(sess))
    return jsonify({"status": "ok"}), 200

@app.route("/api/session/<sid>/surveys", methods=["GET"])
def get_surveys(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(json.loads(stored)["users"]), 200

@app.route("/api/session/<sid>/settings", methods=["POST"])
def update_settings(sid):
    data = request.json
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    
    session_data = json.loads(stored)
    session_data["settings"].update(data)
    redis_client.set(sid, json.dumps(session_data))
    return jsonify({"status": "ok"}), 200

@app.route("/api/session/<sid>/teams", methods=["POST"])
def generate_teams_endpoint(sid):
    stored = redis_client.get(sid)
    if not stored:
        return jsonify({"error": "Session not found"}), 404
    
    session_data = json.loads(stored)
    users = session_data["users"]
    request_data = request.json
    
    if len(users) < 2:
        return jsonify({"error": "Need at least 2 users to form teams"}), 400
    
    print(f"Generating teams for {len(users)} users")
    print(f"User data: {users}")
    print(f"Request settings: {request_data.get('settings')}")
    
    # Convert users to DataFrame for team formation
    df = pd.DataFrame(users)
    
    # Use settings from request if provided, otherwise use stored settings
    settings = request_data.get('settings', session_data["settings"])
    
    # Form teams based on settings
    teams = make_teams(
        df, 
        settings["team_size"], 
        settings["team_approach"],
        settings["characteristics"],
        settings["similarity_threshold"]
    )
    
    # Store teams in session data
    session_data["teams"] = teams
    redis_client.set(sid, json.dumps(session_data))
    
    # Format teams for response
    formatted_teams = []
    for team in teams:
        team_members = []
        for member in team["members"]:
            # Use the original member data without defaults
            team_members.append(member)
        formatted_teams.append({
            "members": team_members,
            "metrics": team["metrics"]
        })
    
    print(f"Formatted teams: {formatted_teams}")
    return jsonify({"teams": formatted_teams}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
