import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sign', methods=['POST'])
def sign():
    data = request.get_json()
    print("📦 Received from Sheets:", data)

    return jsonify({
        "status": "success",
        "message": "Hello from Render!",
        "echo": data
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
