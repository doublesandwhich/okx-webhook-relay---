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

# 🔐 Log secrets for debugging (safe in dev, remove in prod)
print("🔐 Loaded secrets:")
print("OKX_API_KEY:", os.getenv("OKX_API_KEY"))
print("OKX_API_SECRET:", os.getenv("OKX_API_SECRET"))
print("OKX_API_PASSPHRASE:", os.getenv("OKX_API_PASSPHRASE"))

def sign_okx_request(timestamp, method, endpoint, body):
    secret = os.getenv("OKX_API_SECRET")
    assert secret is not None, "❌ Missing OKX_API_SECRET"
    prehash = f"{timestamp}{method.upper()}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(secret.encode(), prehash.encode(), hashlib.sha256).digest()
    ).decode()
    return signature

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.get_json(force=True)
        print("📦 Incoming payload:", json.dumps(payload, indent=2))

        url = payload.get("url")
        method = payload.get("method", "POST")
        body = payload.get("body", {})
        meta = payload.get("meta", {})

        # ✅ Enforce demo endpoint
        if "api.okx.com" in url:
            return jsonify({"error": "❌ Live endpoint not allowed"}), 400

        assert os.getenv("OKX_API_KEY"), "❌ Missing OKX_API_KEY"
        assert os.getenv("OKX_API_PASSPHRASE"), "❌ Missing OKX_API_PASSPHRASE"

        endpoint = url.replace("https://www.okx.com", "")
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
        coin = meta.get("coin")
        balances = data.get("data", [])
        qty = next((float(item["balance"]) for item in balances if item.get("ccy") == coin), 0)

        return jsonify({
            "qty": qty,
            "coin": coin,
            "symbol": meta.get("symbol")
        })

    except AssertionError as ae:
        print("❌ Assertion Error:", str(ae))
        return jsonify({"error": str(ae)}), 500
    except Exception as e:
        print("❌ General Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/test-okx', methods=['GET'])
def test_okx():
    try:
        response = requests.get("https://www.okx.com/api/v5/public/instruments?instType=SPOT")
        return jsonify({
            "status": "success",
            "code": response.status_code,
            "data": response.json()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
