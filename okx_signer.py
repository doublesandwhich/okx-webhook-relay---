import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "alive",
        "message": "Flask is running and reachable"
    })

@app.route('/sign', methods=['POST'])
def sign():
    data = request.form.to_dict()
    print("📦 Received form data:", data)

    return jsonify({
        "status": "success",
        "message": "Hello from Render!",
        "echo": data
    })

@app.route('/debug', methods=['GET', 'POST'])
def debug():
    print("🔍 DEBUG ROUTE HIT")
    print("🧾 Headers:", dict(request.headers))
    print("📦 Form:", request.form.to_dict())
    print("📄 Raw Data:", request.get_data(as_text=True))
    print("🧠 JSON:", request.get_json(silent=True))

    return jsonify({
        "status": "debug",
        "method": request.method,
        "headers": dict(request.headers),
        "form": request.form.to_dict(),
        "raw": request.get_data(as_text=True),
        "json": request.get_json(silent=True)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
