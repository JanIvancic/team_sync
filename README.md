# Team Sync

Team Sync is a web application for creating and managing teams based on user surveys.

## Project Structure

- `backend/`: Flask backend with Redis for session management
- `frontend/`: Vue.js frontend

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```
cd backend
```

2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the Flask application:
```
python app.py
```

### Exposing the app with ngrok

```
pip install pyngrok
python run_with_ngrok.py
```
The terminal will display a public URL that forwards traffic to your local
Flask server.

### Frontend Setup

1. Navigate to the frontend directory:
```
cd frontend
```

2. Install dependencies:
```
npm install
```

3. Run the development server:
```
npm run serve
```

## Usage

1. Open the frontend application in your browser (usually at http://localhost:8080)
2. Create a session or join an existing one
3. Fill out the survey
4. Generate teams (if you're the session creator)

## Requirements

- Python 3.6+
- Node.js 12+
- Redis server running on localhost:6379
