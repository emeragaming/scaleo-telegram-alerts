from flask import Flask, request
import os
import pytz
import requests
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "meusegredo123")  # segredo simples

def tg_send(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }, timeout=10)

@app.route("/")
def index():
    return "OK", 200

@app.route("/test")
def test():
    msg = request.args.get("msg", "Teste ok ✅")
    tg_send(msg)
    return "Sent", 200

@app.route("/webhook/scaleo", methods=["POST"])
def webhook_scaleo():
    token = request.args.get("token")
    if token != WEBHOOK_TOKEN:
        return "Unauthorized", 403

    data = request.json or {}
    # Extrair dados importantes do webhook
    offer_name = data.get("offer", {}).get("title") or data.get("offer_title", "N/A")
    affiliate_name = data.get("affiliate", {}).get("company") or data.get("affiliate_name", "N/A")
    goal_title = data.get("goal", {}).get("title") or data.get("goal_title", "CPA")
    click_id = data.get("click_id", data.get("click", {}).get("id", "N/A"))
    fraud_score = data.get("fraud_score", data.get("fraud", {}).get("score", "N/A"))
    ip_addr = data.get("ip", data.get("visitor", {}).get("ip", "N/A"))
    geo = data.get("geo", data.get("location", {}).get("country", "N/A"))
    device_type = data.get("device_type", data.get("device", {}).get("type", "N/A"))
    device_os = data.get("device_os", data.get("device", {}).get("os", "N/A"))
    lang = data.get("language", data.get("visitor", {}).get("language", "N/A"))
    conn = data.get("connection_type", data.get("connection", {}).get("type", "N/A"))
    carrier = data.get("mobile_operator", data.get("carrier", "N/A"))

    # Converter hora para Europe/Malta
    tz = pytz.timezone("Europe/Malta")
    mt_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M")

    text = (
        "✅ *Conversion Details* ✅\n\n"
        f"Nova conversão: *{goal_title}*\n"
        f"Data Hora: {mt_time} (Europe/Malta)\n"
        f"Affiliate: {affiliate_name}\n"
        f"Offer: {offer_name}\n"
        "Total de Conversões (CPA) – *This Month*: 🚀 (a implementar)\n"
        "____________________________\n\n"
        "⚠️ *Fraud Check* ⚠️\n\n"
        f"Click ID: {click_id}\n"
        f"Fraud Score: {fraud_score}\n"
        f"IP: {ip_addr}\n"
        f"Geo: {geo}\n"
        f"Device Type: {device_type}\n"
        f"Device OS: {device_os}\n"
        f"Language: {lang}\n"
        f"Connection Type: {conn}\n"
        f"Mobile Operator: {carrier}"
    )

    tg_send(text)
    return "ok", 200
