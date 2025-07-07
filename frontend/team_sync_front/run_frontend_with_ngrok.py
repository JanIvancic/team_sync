import subprocess
import time
import sys
import os

def run_ngrok_for_frontend():
    try:
        # Start ngrok tunnel for frontend (port 8080)
        print("Starting ngrok tunnel for frontend...")
        ngrok_process = subprocess.Popen([
            "ngrok", "http", "8080", "--bind-tls=true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("ngrok tunnel started for frontend on port 8080")
        print("You can now access your frontend via the ngrok URL")
        print("Make sure your frontend is running with: npm run serve")
        
        # Keep the script running
        try:
            ngrok_process.wait()
        except KeyboardInterrupt:
            print("\nStopping ngrok tunnel...")
            ngrok_process.terminate()
            ngrok_process.wait()
            print("ngrok tunnel stopped")
            
    except FileNotFoundError:
        print("Error: ngrok not found. Please install ngrok first.")
        print("Download from: https://ngrok.com/download")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ngrok_for_frontend() 