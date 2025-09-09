import os
import hmac
import base64
import hashlib
import json
import requests
import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
app = Flask(__name__)

sys.stdout.write("✅ Secrets loaded successfully.\n")
sys.stdout.flush()

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
        sys.stdout.write("📦 Incoming payload:\n" + json.dumps(payload, indent=2) + "\n")
        sys.stdout.flush()

        url = payload.get("url")
        method = payload.get("method", "GET").upper()
        meta = payload.get("meta", {})

        if not url.startswith("https://www.okx.com/api/v5"):
            return jsonify({"error": "❌ Invalid endpoint"}), 400

        assert os.getenv("OKX_API_KEY"), "❌ Missing OKX_API_KEY"
        assert os.getenv("OKX_API_PASSPHRASE"), "❌ Missing OKX_API_PASSPHRASE"

        endpoint = url.replace("https://www.okx.com", "")
        body_str = "" if method == "GET" else json.dumps(payload.get("body", {}))

        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        signature = sign_okx_request(timestamp, method, endpoint, body_str)

        headers = {
            "OK-ACCESS-KEY": os.getenv("OKX_API_KEY"),
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": os.getenv("OKX_API_PASSPHRASE"),
            "Content-Type": "application/json",
            "x-simulated-trading": "1"  # ✅ Enables demo mode
        }

        response = requests.request(method, url, headers=headers)
        sys.stdout.write("📨 OKX response:\n" + response.text + "\n")
        sys.stdout.flush()

        data = response.json()
        coin = meta.get("coin", "").upper()
        balances = data.get("data", [])

        sys.stdout.write("🔍 Coins returned by OKX:\n")
        sys.stdout.flush()
        for item in balances:
            ccy = item.get("ccy", "UNKNOWN")
            sys.stdout.write(f"\n🪙 {ccy}\n")
            for key, val in item.items():
                sys.stdout.write(f"  {key}: {val}\n")
            sys.stdout.flush()

        qty = next(
            (
                float(item.get("cashBal", item.get("availBal", item.get("balance", 0))))
                for item in balances
                if item.get("ccy", "").upper() == coin
            ),
            0
        )

        sys.stdout.write(f"✅ Matched {coin}: Qty {qty}\n")
        sys.stdout.flush()

        return jsonify({
            "qty": qty,
            "coin": coin,
            "symbol": meta.get("symbol")
        })

    except AssertionError as ae:
        sys.stdout.write("❌ Assertion Error: " + str(ae) + "\n")
        sys.stdout.flush()
        return jsonify({"error": str(ae)}), 500
    except Exception as e:
        sys.stdout.write("❌ General Error: " + str(e) + "\n")
        sys.stdout.flush()
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
