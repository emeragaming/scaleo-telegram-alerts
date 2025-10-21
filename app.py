from flask import Flask, request
import os
import pytz
import requests
from datetime import datetime

app = Flask(__name__)  # <-- garante que o 'app' existe

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "meusegredo123")

def tg_send(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=10,
    )

@app.route("/")
def index():
    return "OK", 200

@app.route("/test")
def test():
    msg = request.args.get("msg", "Teste ok ✅")
    tg_send(msg)
    return "Sent", 200

# ===== WEBHOOK EM MODO DEBUG =====
@app.route("/webhook/scaleo", methods=["POST"])
def webhook_scaleo():
    # validação simples por token na query: ...?token=meusegredo123
    token = request.args.get("token")
    if token != WEBHOOK_TOKEN:
        print("Webhook refused: bad token", token)
        return "Unauthorized", 403

    # capturar tudo para diagnóstico
    raw_body = request.get_data(as_text=True) or ""
    headers = dict(request.headers)
    form = request.form.to_dict(flat=True)
    json_body = request.get_json(silent=True)

    print("=== SCALEO WEBHOOK HIT ===")
    print("Headers:", headers)
    print("Raw:", raw_body)
    print("Form:", form)
    print("JSON:", json_body)

    # ping de debug para o Telegram
    try:
        tg_send("🔔 Webhook recebido do Scaleo (debug).")
    except Exception as e:
        print("Telegram error on debug ping:", e)

    # normalizar dados (JSON > form)
    data = json_body if isinstance(json_body, dict) else form

    def pick(*paths, default="N/A"):
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

    offer_name     = pick(("offer","title"), ("offer_title",), ("offer_id",))
    affiliate_name = pick(("affiliate","company"), ("affiliate_name",), ("affiliate_id",))
    goal_title     = pick(("goal","title"), ("goal_title",), default="CPA")
    click_id       = pick(("click","id"), ("click_id",), ("clickid",))
    fraud_score    = pick(("fraud","score"), ("fraud_score",))
    ip_addr        = pick(("visitor","ip"), ("ip",))
    geo            = pick(("location","country"), ("geo",))
    device_type    = pick(("device","type"), ("device_type",))
    device_os      = pick(("device","os"), ("device_os",))
    lang           = pick(("visitor","language"), ("language",))
    conn           = pick(("connection","type"), ("connection_type",))
    carrier        = pick(("mobile_operator",), ("carrier",))

    # hora Europe/Malta
    mt = pytz.timezone("Europe/Malta")
    mt_time = datetime.now(mt).strftime("%Y-%m-%d %H:%M")

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
    try:
        tg_send(text)
    except Exception as e:
        print("Telegram error on final send:", e)

    return "ok", 200
