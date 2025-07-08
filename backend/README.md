# Team Sync Backend

## Setup
1. Create a virtual environment:
```
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```
venv\Scripts\activate
```
- macOS/Linux:
```
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Copy the example environment file and adjust values if needed:
```
cp .env.example .env
```
5. Run the Flask application:
```
python app.py
```

## API Endpoints

- `POST /api/session`: Create a new session
- `POST /api/session/<sid>/survey`: Submit a survey for a user
- `GET /api/session/<sid>/surveys`: Get all surveys for a session
- `POST /api/session/<sid>/teams`: Generate teams for a session

## Notes
- Make sure Redis is running on localhost:6379
- The application will run on http://localhost:5000
