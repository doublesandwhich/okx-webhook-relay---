import os
import time
import hmac
import base64
import hashlib
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def sign_okx_request(timestamp, method, endpoint, body):
    secret = os.getenv("OKX_API_SECRET")
    prehash = f"{timestamp}{method.upper()}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(secret.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()
    return signature

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.get_json(force=True)
        print("📦 Incoming payload:", payload)

        url = payload.get("url")
        method = payload.get("method", "POST")
        body = payload.get("body", {})
        meta = payload.get("meta", {})

        # Extract endpoint from full URL
        endpoint = url.replace("https://www.okx.com", "").replace("https://api.okx.com", "")
        body_str = json.dumps(body) if method.upper() != "GET" else ""

        timestamp = str(time.time())
        signature = sign_okx_request(timestamp, method, endpoint, body_str)

        headers = {
            "OK-ACCESS-KEY": os.getenv("OKX_API_KEY"),
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": os.getenv("OKX_API_PASSPHRASE"),
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, headers=headers, json=body)
        print("📨 OKX response:", response.text)

        data = response.json()
        qty = float(data.get("data", [{}])[0].get("balance", 0))
        price = 1.0  # Placeholder — replace with actual price lookup if needed
        value = qty * price

        return jsonify({
            "price": price,
            "qty": qty,
            "value": value,
            "coin": meta.get("coin"),
            "symbol": meta.get("symbol")
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
