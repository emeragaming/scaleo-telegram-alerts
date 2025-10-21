from flask import Flask, request
import os
import requests
import pytz
from datetime import datetime
from threading import Thread

app = Flask(__name__)

# --- Environment ---
BOT_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID       = os.environ.get("TELEGRAM_CHAT_ID", "")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "meusegredo123")  # muda no Render

# --- Telegram (async) ---
def tg_send(text: str):
    """Envia mensagem para o Telegram (com timeout curto)."""
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=5,
        )
    except Exception as e:
        print("Telegram send error:", e)

def send_async(text: str):
    Thread(target=tg_send, args=(text,), daemon=True).start()

# --- Helpers ---
def pick(data: dict | None, *paths, default="N/A"):
    """Vai buscar um valor em dicts aninhados; aceita vários caminhos possíveis."""
    d = data or {}
    for path in paths:
        cur = d
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and cur not in (None, ""):
            return cur
    return default

def malta_now_str():
    tz = pytz.timezone("Europe/Malta")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M")

# --- Routes ---
@app.route("/")
def index():
    return "OK", 200

@app.route("/test")
def test():
    msg = request.args.get("msg", "Teste ok ✅")
    send_async(msg)
    return "Sent", 200

@app.route("/webhook/scaleo", methods=["POST"])
def webhook_scaleo():
    # Validação simples por token na query: .../webhook/scaleo?token=SEU_TOKEN
    token = request.args.get("token")
    if token != WEBHOOK_TOKEN:
        return "Unauthorized", 403

    # Aceitar JSON ou form (algumas instalações enviam como form-encoded)
    raw_json = request.get_json(silent=True)
    form = request.form.to_dict(flat=True)
    data = raw_json if isinstance(raw_json, dict) else form

    # Extrair campos (tolerante a chaves diferentes)
    offer_name      = pick(data, ("offer","title"), ("offer_title",), ("offer_name",), ("offer_id",))
    affiliate_name  = pick(data, ("affiliate","company"), ("affiliate_name",), ("affiliate_id",))
    goal_title      = pick(data, ("goal","title"), ("goal_title",), default="CPA")

    click_id        = pick(data, ("click","id"), ("click_id",), ("clickid",))
    fraud_score     = pick(data, ("fraud","score"), ("fraud_score",))
    ip_addr         = pick(data, ("visitor","ip"), ("ip",))
    geo             = pick(data, ("location","country"), ("geo",))
    device_type     = pick(data, ("device","type"), ("device_type",))
    device_os       = pick(data, ("device","os"), ("device_os",))
    lang            = pick(data, ("visitor","language"), ("language",))
    conn            = pick(data, ("connection","type"), ("connection_type",))
    carrier         = pick(data, ("mobile_operator",), ("carrier",))

    # Hora Europe/Malta
    mt_time = malta_now_str()

    # Mensagem
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

    # Responder rápido ao Scaleo e enviar para o Telegram em background
    send_async(text)
    return "ok", 200

# Gunicorn usa 'app:app'
# (Nada a fazer aqui)
