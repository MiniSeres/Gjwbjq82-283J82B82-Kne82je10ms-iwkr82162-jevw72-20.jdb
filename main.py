from flask import Flask, jsonify, request
from flask_cors import CORS
import json, hashlib, secrets, os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/api/register', methods=['POST'])
def register():
    data = load_data()
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({"error": "Thiếu thông tin"}), 400
    if username in data["users"]:
        return jsonify({"error": "Tên đã tồn tại"}), 400
    
    data["users"][username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "created": datetime.now().isoformat()
    }
    save_data(data)
    return jsonify({"success": True, "message": "Đăng ký thành công!"})

@app.route('/api/login', methods=['POST'])
def login():
    data = load_data()
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = data["users"].get(username)
    if not user:
        return jsonify({"error": "Sai tên hoặc mật khẩu"}), 401
    if user["password"] != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({"error": "Sai tên hoặc mật khẩu"}), 401
    
    token = secrets.token_hex(32)
    return jsonify({"success": True, "token": token, "username": username})

@app.route('/api/verify', methods=['GET'])
def verify():
    token = request.headers.get('X-Token')
    if not token:
        return jsonify({"valid": False}), 401
    # Ở bản đơn giản, token chỉ tồn tại trong client, server không lưu token
    return jsonify({"valid": True})

@app.route('/api/stats', methods=['GET'])
def stats():
    data = load_data()
    return jsonify({"users": len(data["users"])})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
