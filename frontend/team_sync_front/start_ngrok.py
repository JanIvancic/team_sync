from pyngrok import ngrok
import time

print("Starting ngrok tunnel for frontend on port 8080...")
public_url = ngrok.connect(8080, bind_tls=True).public_url
print(f"Frontend ngrok URL: {public_url}")
print("Keep this terminal open to maintain the tunnel.")
print("Press Ctrl+C to stop the tunnel.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping ngrok tunnel...")
    ngrok.kill()
    print("Tunnel stopped.") 