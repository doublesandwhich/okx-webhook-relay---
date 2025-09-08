import os
import time
import hmac
import base64
import hashlib
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.get_json(force=True)
        print("📦 Incoming payload:", payload)

        # Extract fields
        url = payload.get("url")
        method = payload.get("method", "POST")
        body = payload.get("body", {})
        meta = payload.get("meta", {})

        # Prepare OKX signature
        timestamp = str(time.time())
        body_str = "" if method == "GET" else json.dumps(body)
        prehash = f"{timestamp}{method.upper()}{url.replace('https://api.okx.com', '')}{body_str}"
        secret = os.getenv("OKX_API_SECRET")
        signature = base64.b64encode(hmac.new(
            secret.encode(), prehash.encode(), hashlib.sha256
        ).digest()).decode()

        headers = {
            "OK-ACCESS-KEY": os.getenv("OKX_API_KEY"),
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": os.getenv("OKX_API_PASSPHRASE"),
            "Content-Type": "application/json"
        }

        # Send request to OKX
        response = requests.post(url, headers=headers, json=body)
        print("📨 OKX response:", response.text)

        # Parse response (example assumes balance structure)
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
