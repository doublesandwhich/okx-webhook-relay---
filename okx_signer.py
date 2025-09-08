import os
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment
API_KEY = os.getenv("OKX_API_KEY")
API_SECRET = os.getenv("OKX_API_SECRET")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Webhook is running. Use POST /sign to get a signature."
    })

@app.route('/sign', methods=['POST'])
def sign():
    data = request.get_json()

    # Log the incoming payload for inspection
    print("📦 Received payload:", data)

    # Extract required fields
    payload = data.get('payload')
    secret = data.get('secret', API_SECRET)  # fallback to .env secret if not provided

    if not payload or not secret:
        print("⚠️ Missing payload or secret")
        return jsonify({
            "status": "error",
            "message": "Missing payload or secret"
        }), 400

    try:
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Encode to Base64
        encoded = base64.b64encode(signature).decode('utf-8')

        # Return as JSON
        return jsonify({
            "status": "success",
            "message": "Payload signed successfully",
            "signature": encoded,
            "api_key": API_KEY,
            "passphrase": PASSPHRASE
        })

    except Exception as e:
        print("❌ Error generating signature:", str(e))
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
