# backend/app.py

import os
import random
import json
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from redis import Redis
from dotenv import load_dotenv
from team_logic import make_teams
import numpy as np
from datetime import datetime, timedelta
from whitenoise import WhiteNoise
import uuid
import sys
import traceback

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
        "origins": [
            "http://localhost:8080",
            "http://localhost:8081",
            "https://team-sync-app.herokuapp.com",
            "https://team-sync-app-8aa47d5c9ba6.herokuapp.com"
        ],
        "methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Try to connect to Redis, fall back to in-memory storage if not available
try:
    redis_url = os.environ.get('REDISCLOUD_URL')
    if not redis_url:
        print("No REDISCLOUD_URL found, falling back to in-memory storage")
        redis_client = None
    else:
        print(f"Attempting to connect to Redis Cloud at {redis_url}")
        redis_client = Redis.from_url(redis_url)
        # Test the connection
        redis_client.ping()
        print("Successfully connected to Redis Cloud")
except Exception as e:
    print(f"Failed to connect to Redis: {str(e)}")
    print("Full error:", traceback.format_exc())
    print("Falling back to in-memory storage")
    redis_client = None

# In-memory storage for sessions
sessions = {}

def get_redis_key(key):
    if redis_client:
        return redis_client.get(key)
    return sessions.get(key)

def set_redis_key(key, value, expire_seconds=None):
    try:
        if redis_client:
            if expire_seconds:
                redis_client.setex(key, expire_seconds, value)
            else:
                redis_client.set(key, value)
            print(f"Successfully set Redis key: {key}")
        else:
            sessions[key] = value
            print(f"Stored in memory: {key}")
    except Exception as e:
        print(f"Error setting Redis key {key}: {str(e)}")
        print("Full error:", traceback.format_exc())
        # Fall back to in-memory storage
        sessions[key] = value
        print(f"Fallback: Stored in memory: {key}")

def delete_redis_key(key):
    if redis_client:
        redis_client.delete(key)
    else:
        sessions.pop(key, None)

def get_session(sid):
    if redis_client:
        data = redis_client.get(f"session:{sid}")
        return json.loads(data) if data else None
    return sessions.get(sid)

def set_session(sid, data):
    if redis_client:
        redis_client.set(f"session:{sid}", json.dumps(data))
    else:
        sessions[sid] = data

def generate_session_id():
    """Generate a 6-digit session ID."""
    return ''.join(random.choices('0123456789', k=6))

@app.route("/")
def serve():
    return send_from_directory(static_folder, 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(static_folder, path)

@app.route("/api/session", methods=["POST"])
def create_session():
    try:
        session_id = generate_session_id()
        # Keep generating until we get a unique ID
        while get_redis_key(f'session:{session_id}'):
            session_id = generate_session_id()
            
        data = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'surveys': [],
            'teams': [],
            'settings': {
                'anonymous_mode': False,
                'show_teams_to_users': True,
                'team_size': 4
            }
        }
        print(f"Creating new session with ID: {session_id}")
        set_redis_key(f'session:{session_id}', json.dumps(data))
        return jsonify(data)
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        print("Full error:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    data = get_redis_key(f'session:{session_id}')
    if data:
        return jsonify(json.loads(data))
    return jsonify({'error': 'Session not found'}), 404

@app.route("/api/session/<session_id>/survey", methods=["POST"])
def submit_survey(session_id):
    data = request.json
    session_data = get_redis_key(f'session:{session_id}')
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = json.loads(session_data)
    session_data['surveys'].append(data)
    set_redis_key(f'session:{session_id}', json.dumps(session_data))
    return jsonify(session_data)

@app.route("/api/session/<session_id>/teams", methods=["POST"])
def generate_teams(session_id):
    session_data = get_redis_key(f'session:{session_id}')
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = json.loads(session_data)
    surveys = session_data['surveys']
    if not surveys:
        return jsonify({'error': 'No surveys submitted'}), 400
    
    df = pd.DataFrame(surveys)
    teams = make_teams(df, session_data['settings']['team_size'])
    session_data['teams'] = teams
    set_redis_key(f'session:{session_id}', json.dumps(session_data))
    return jsonify(session_data)

@app.route("/api/session/<session_id>/settings", methods=["GET", "PUT", "POST"])
def handle_settings(session_id):
    if request.method == "GET":
        session_data = get_redis_key(f'session:{session_id}')
        if not session_data:
            return jsonify({"error": "Session not found"}), 404
        
        session_data = json.loads(session_data)
        return jsonify(session_data.get("settings", {})), 200
    
    elif request.method in ["PUT", "POST"]:
        data = request.json
        session_data = get_redis_key(f'session:{session_id}')
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = json.loads(session_data)
        session_data['settings'].update({
            'anonymous_mode': data.get('anonymous_mode', False),
            'show_teams_to_users': data.get('show_teams_to_users', True),
            'team_size': data.get('team_size', 4),
            'team_approach': data.get('team_approach', 'homogeni'),
            'characteristics': data.get('characteristics', ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"]),
            'similarity_threshold': data.get('similarity_threshold', 50)
        })
        set_redis_key(f'session:{session_id}', json.dumps(session_data))
        return jsonify(session_data)

@app.route("/api/session/<sid>/surveys", methods=["GET"])
def get_surveys(sid):
    session_data = get_redis_key(f'session:{sid}')
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    session_data = json.loads(session_data)
    return jsonify(session_data.get("surveys", [])), 200

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
