import requests

SERVER_URL = "http://127.0.0.1:8000/api/whatsapp/webhook"

def test_message(msg):
    print(f"\n[WhatsApp User]: {msg}")
    try:
        resp = requests.post(SERVER_URL, data={"Body": msg, "From": "whatsapp:+919876543210"})
        print(f"[AI Saathi Bot]: {resp.text}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    print("=== AI Saathi: WhatsApp Bot Simulator ===")
    test_message("नमस्ते, मुझे सरकारी योजनाओं के बारे में जानना है")
    test_message("Dear customer your electricity power will be disconnected call 9876543210")
    test_message("1")
