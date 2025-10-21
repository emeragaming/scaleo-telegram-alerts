@app.route("/webhook/scaleo", methods=["POST"])
def webhook_scaleo():
    # ✅ Confere o token na query (garante que é EXACTAMENTE o mesmo que puseste no Render)
    token = request.args.get("token")
    if token != WEBHOOK_TOKEN:
        print("Webhook refused: bad token", token)
        return "Unauthorized", 403

    # 🔎 Recolhe o bruto + headers para sabermos o que o Scaleo está a enviar
    raw_body = request.get_data(as_text=True) or ""
    headers = dict(request.headers)
    form = request.form.to_dict(flat=True)
    json_body = None
    try:
        json_body = request.get_json(silent=True)
    except Exception:
        json_body = None

    print("=== SCALEO WEBHOOK HIT ===")
    print("Headers:", headers)
    print("Raw:", raw_body)
    print("Form:", form)
    print("JSON:", json_body)

    # Envia um ping mínimo ao Telegram só para confirmar recepção
    try:
        tg_send("🔔 Webhook recebido do Scaleo (debug).")
    except Exception as e:
        print("Telegram error on debug ping:", e)

    # Tenta normalizar dados, aceitando JSON ou form
    data = json_body if isinstance(json_body, dict) else form

    def pick(*paths, default="N/A"):
        d = data or {}
        for p in paths:
            cur = d
            ok = True
            for k in p:
                if isinstance(cur, dict) and k in cur:
                    cur = cur[k]
                else:
                    ok = False
                    break
            if ok and cur not in (None, ""):
                return cur
        return default

    offer_name    = pick(("offer","title"), ("offer_title",), ("offer_id",))
    affiliate_name= pick(("affiliate","company"), ("affiliate_name",), ("affiliate_id",))
    goal_title    = pick(("goal","title"), ("goal_title",), default="CPA")
    click_id      = pick(("click","id"), ("click_id",), ("clickid",))
    fraud_score   = pick(("fraud","score"), ("fraud_score",))
    ip_addr       = pick(("visitor","ip"), ("ip",))
    geo           = pick(("location","country"), ("geo",))
    device_type   = pick(("device","type"), ("device_type",))
    device_os     = pick(("device","os"), ("device_os",))
    lang          = pick(("visitor","language"), ("language",))
    conn          = pick(("connection","type"), ("connection_type",))
    carrier       = pick(("mobile_operator",), ("carrier",))

    # Hora Europe/Malta
    import pytz
    from datetime import datetime
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
