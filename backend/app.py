# backend/app.py

import os
import random
import json
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from redis import Redis
from dotenv import load_dotenv
from .team_logic import make_teams
import numpy as np
from datetime import datetime
from whitenoise import WhiteNoise

load_dotenv()

# Get the absolute path for static files
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_folder = os.path.join(root_dir, 'static')
print(f"Root directory: {root_dir}")
print(f"Static folder path: {static_folder}")
print(f"Static folder exists: {os.path.exists(static_folder)}")
if os.path.exists(static_folder):
    print(f"Static folder contents: {os.listdir(static_folder)}")

app = Flask(__name__, static_folder=static_folder, static_url_path='')
# Add Whitenoise for static files
app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_folder)

# Configure CORS with Heroku domain
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080", "http://localhost:8081", "https://team-sync-app-8aa47d5c9ba6.herokuapp.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize in-memory storage as fallback
session_storage = {}

# Configure Redis with fallback to in-memory storage
try:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    # Test Redis connection
    redis_client.ping()
    print("Successfully connected to Redis")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    print("Falling back to in-memory storage")
    redis_client = None

def get_session(sid):
    if redis_client:
        try:
            stored = redis_client.get(sid)
            return json.loads(stored) if stored else None
        except Exception as e:
            print(f"Redis error: {e}")
            return session_storage.get(sid)
    return session_storage.get(sid)

def set_session(sid, data):
    if redis_client:
        try:
            redis_client.set(sid, json.dumps(data))
        except Exception as e:
            print(f"Redis error: {e}")
            session_storage[sid] = data
    else:
        session_storage[sid] = data

def generate_session_id():
    return str(random.randint(100000, 999999))

@app.route("/api/session", methods=["POST"])
def create_session():
    sid = generate_session_id()
    set_session(sid, {
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
    })
    return jsonify({"session_id": sid}), 201

@app.route("/api/session/<sid>/survey", methods=["POST"])
def submit_survey(sid):
    data = request.json
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    
    # If anonymous mode is enabled, generate a random ID for the user
    if sess["settings"]["anonymous_mode"]:
        user_id = f"user_{len(sess['users']) + 1}"
        data["id"] = user_id
        data["name"] = f"User {len(sess['users']) + 1}"
    
    sess["users"].append(data)
    set_session(sid, sess)
    return jsonify({"status": "ok", "user_id": data.get("id")}), 200

@app.route("/api/session/<sid>/surveys", methods=["GET"])
def get_surveys(sid):
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(sess["users"]), 200

@app.route("/api/session/<sid>/settings", methods=["POST"])
def update_settings(sid):
    data = request.json
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    
    sess["settings"].update(data)
    set_session(sid, sess)
    return jsonify({"status": "ok"}), 200

@app.route("/api/session/<sid>/settings", methods=["GET"])
def get_settings(sid):
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(sess["settings"]), 200

@app.route("/api/session/<sid>/teams", methods=["POST"])
def generate_teams_endpoint(sid):
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    
    users = sess["users"]
    request_data = request.json
    
    if len(users) < 2:
        return jsonify({"error": "Need at least 2 users to form teams"}), 400
    
    print(f"Generating teams for {len(users)} users")
    print(f"User data: {users}")
    print(f"Request settings: {request_data.get('settings')}")
    
    # Convert users to DataFrame for team formation
    df = pd.DataFrame(users)
    
    # Use settings from request if provided, otherwise use stored settings
    settings = request_data.get('settings', sess["settings"])
    
    # Form teams based on settings
    teams = make_teams(
        df, 
        settings["team_size"], 
        settings["team_approach"],
        settings["characteristics"],
        settings["similarity_threshold"]
    )
    
    # Store teams in session data
    sess["teams"] = teams
    set_session(sid, sess)
    
    # Format teams for response
    formatted_teams = []
    for team in teams:
        team_members = []
        for member in team["members"]:
            # Find the original user data by matching the skills
            original_user = next((u for u in users if all(u.get(k) == member.get(k) for k in member.keys() if k not in ['id', 'name'])), member)
            # Preserve the original user's ID and name
            member_with_id = {
                'id': original_user.get('id', f'user_{len(team_members) + 1}'),
                'name': original_user.get('name', f'User {len(team_members) + 1}'),
                **member
            }
            team_members.append(member_with_id)
        formatted_teams.append({
            "members": team_members,
            "metrics": team["metrics"]
        })
    
    print(f"Formatted teams: {formatted_teams}")
    return jsonify({"teams": formatted_teams}), 200

@app.route("/api/session/<sid>/teams", methods=["GET"])
def get_teams(sid):
    sess = get_session(sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    
    teams = sess.get("teams", [])
    
    # Format teams for response
    formatted_teams = []
    for team in teams:
        team_members = []
        for member in team["members"]:
            # In anonymous mode, preserve the user ID but use generic names
            if sess["settings"]["anonymous_mode"]:
                member = member.copy()
                # Only update the name, keep the ID
                member["name"] = f"User {member.get('id', '').split('_')[1] if member.get('id') else 'Unknown'}"
            team_members.append(member)
        formatted_teams.append({
            "members": team_members,
            "metrics": team["metrics"]
        })
    
    return jsonify({"teams": formatted_teams}), 200

# Debug route to check application status
@app.route('/debug')
def debug():
    return jsonify({
        'static_folder': app.static_folder,
        'static_folder_exists': os.path.exists(app.static_folder),
        'static_folder_contents': os.listdir(app.static_folder) if os.path.exists(app.static_folder) else [],
        'root_path': app.root_path,
        'instance_path': app.instance_path
    })

# Serve static files and SPA routes
@app.route('/')
def root():
    try:
        print(f"Serving index.html from {app.static_folder}")
        if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
            print(f"index.html not found in {app.static_folder}")
            return jsonify({'error': 'index.html not found'}), 404
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        print(f"Requested path: {path}")
        full_path = os.path.join(app.static_folder, path)
        print(f"Full path: {full_path}")
        print(f"Path exists: {os.path.exists(full_path)}")
        
        if os.path.exists(full_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Error serving {path}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
