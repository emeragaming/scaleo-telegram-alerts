from flask import Flask, request
import os, requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

def tg_send(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)

@app.route("/")
def index():
    return "OK", 200

@app.route("/test")
def test():
    msg = request.args.get("msg", "Teste ok ✅")
    tg_send(msg)
    return "Sent", 200
