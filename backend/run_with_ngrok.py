import threading
from pyngrok import ngrok
from app import app

if __name__ == "__main__":
    public_url = ngrok.connect(5000, bind_tls=True).public_url
    print(f"ngrok tunnel: {public_url}")

    def run_app():
        app.run(host="0.0.0.0", port=5000)

    thread = threading.Thread(target=run_app)
    thread.start()
    thread.join()
