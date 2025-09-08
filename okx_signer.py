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
    try:
        # Try to parse JSON first
        data = request.get_json(force=True)
    except:
        # Fallback to form data if JSON fails
        data = request.form.to_dict()

    print("📦 Received from Sheets:", data)

    return jsonify({
        "status": "success",
        "message": "Hello from Render!",
        "echo": data
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
