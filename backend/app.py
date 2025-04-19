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
        "origins": ["*"],  # Allow all origins in production
        "methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Try to connect to Redis, fall back to in-memory storage if not available
try:
    redis_url = os.environ.get('REDISCLOUD_URL') or os.environ.get('REDIS_URL')
    if not redis_url:
        print("No Redis URL found, falling back to in-memory storage")
        redis_client = None
    else:
        print(f"Attempting to connect to Redis at {redis_url}")
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        # Test the connection
        redis_client.ping()
        print("Successfully connected to Redis")
except Exception as e:
    print(f"Failed to connect to Redis: {str(e)}")
    print("Full error:", traceback.format_exc())
    print("Falling back to in-memory storage")
    redis_client = None

# In-memory storage for sessions
sessions = {}

def get_redis_key(key):
    try:
        if redis_client:
            value = redis_client.get(key)
            return value if value else None
        return sessions.get(key)
    except Exception as e:
        print(f"Error getting Redis key {key}: {str(e)}")
        return sessions.get(key)

def set_redis_key(key, value, expire_seconds=None):
    try:
        if redis_client:
            if expire_seconds:
                redis_client.setex(key, expire_seconds, value)
            else:
                redis_client.set(key, value)
        sessions[key] = value
    except Exception as e:
        print(f"Error setting Redis key {key}: {str(e)}")
        sessions[key] = value

def delete_redis_key(key):
    if redis_client:
        redis_client.delete(key)
    else:
        sessions.pop(key, None)

def get_session_data(sid):
    try:
        if redis_client:
            data = redis_client.get(f"session:{sid}")
            return json.loads(data) if data else None
        return sessions.get(sid)
    except Exception as e:
        print(f"Error getting session {sid}: {str(e)}")
        return sessions.get(sid)

def set_session(sid, data):
    try:
        if redis_client:
            redis_client.set(f"session:{sid}", json.dumps(data))
        sessions[sid] = data
    except Exception as e:
        print(f"Error setting session {sid}: {str(e)}")
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
    try:
        data = request.json
        session_data = get_redis_key(f'session:{session_id}')
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        session_data = json.loads(session_data)
        
        # Generate a unique ID for this survey if not provided
        if 'id' not in data:
            data['id'] = f'user_{len(session_data["surveys"])}'
            
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
            
        session_data['surveys'].append(data)
        set_redis_key(f'session:{session_id}', json.dumps(session_data))
        
        # Return the updated survey with its ID
        return jsonify({
            'survey': data,
            'surveys': session_data['surveys']
        })
    except Exception as e:
        print(f"Error submitting survey: {str(e)}")
        print("Full error:", traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/session/<session_id>/teams", methods=["POST"])
def generate_teams(session_id):
    try:
        session_data = get_session_data(session_id)
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        surveys = session_data.get('surveys', [])
        if not surveys:
            return jsonify({'error': 'No surveys submitted'}), 400
        
        # Get settings from request body if provided, otherwise use session settings
        request_settings = request.json.get('settings', {}) if request.json else {}
        settings = session_data.get('settings', {})
        settings.update(request_settings)  # Update with any provided settings
        
        team_size = int(settings.get('team_size', 4))
        team_approach = settings.get('team_approach', 'homogeni')
        characteristics = settings.get('characteristics', ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"])
        similarity_threshold = float(settings.get('similarity_threshold', 50))
        
        print(f"Generating teams with settings:")
        print(f"- Team size: {team_size}")
        print(f"- Team approach: {team_approach}")
        print(f"- Characteristics: {characteristics}")
        print(f"- Similarity threshold: {similarity_threshold}")
        print(f"Number of surveys: {len(surveys)}")
        
        # Create DataFrame with survey data
        df = pd.DataFrame(surveys)
        print(f"Survey data shape: {df.shape}")
        print(f"Survey data columns: {df.columns.tolist()}")
        
        # Generate teams
        teams = make_teams(
            users=surveys,  # Pass the raw survey data
            team_size=team_size,
            team_approach=team_approach,
            characteristics=characteristics,
            similarity_threshold=similarity_threshold
        )
        
        if not teams:
            return jsonify({'error': 'Failed to generate teams'}), 500
            
        # Format teams with member details
        formatted_teams = []
        for team in teams:
            team_members = []
            for member_id in team:
                member_data = next((s for s in surveys if s.get('id') == member_id), None)
                if member_data:
                    team_members.append({
                        'id': member_id,
                        'name': member_data.get('name', member_id)
                    })
            if team_members:  # Only add teams that have members
                formatted_teams.append(team_members)
            
        print(f"Generated teams: {json.dumps(formatted_teams, indent=2)}")
        
        session_data['teams'] = formatted_teams
        set_session(session_id, session_data)
        return jsonify(session_data)
    except Exception as e:
        print(f"Error generating teams: {str(e)}")
        print("Full error:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

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

@app.route("/api/session/<session_id>/teams", methods=["GET"])
def get_teams(session_id):
    try:
        # Use get_redis_key helper instead of direct redis_client access
        session_data = get_redis_key(f'session:{session_id}')
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
            
        # Parse JSON if it's a string
        if isinstance(session_data, str):
            try:
                session_data = json.loads(session_data)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid session data format'}), 500
                
        # Get teams and settings
        teams = session_data.get('teams', [])
        settings = session_data.get('settings', {})
        anonymous_mode = settings.get('anonymous_mode', False)
        
        # Format team member names based on anonymous mode
        formatted_teams = []
        for i, team in enumerate(teams):
            formatted_team = []
            for j, member in enumerate(team):
                # Handle case where member might be a string
                if isinstance(member, str):
                    member_id = member
                    member_name = f'Member {j+1}' if anonymous_mode else member
                    formatted_team.append({
                        'id': member_id,
                        'name': member_name
                    })
                else:
                    # Handle case where member is a dictionary
                    if anonymous_mode:
                        formatted_team.append({
                            'id': member.get('id', f'user_{j}'),
                            'name': f'Member {j+1}'
                        })
                    else:
                        formatted_team.append(member)
            formatted_teams.append(formatted_team)
            
        return jsonify(formatted_teams)
    except Exception as e:
        print(f"Error in get_teams: {str(e)}")
        print("Full error:", traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

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
