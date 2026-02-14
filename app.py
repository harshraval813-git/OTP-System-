import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Database Setup
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'otp_project'),
        port=os.getenv('DB_PORT', '3306')
    )

@app.route('/')
def home():
    return "OTP Backend is Running!"

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    otp = str(random.randint(100000, 999999))
    expiry_time = datetime.now() + timedelta(minutes=5)
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO otp_logs (email, otp, expiry_time) VALUES (%s, %s, %s)", (email, otp, expiry_time))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "OTP sent!", "otp": otp}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Yeh line Render ka port error fix karegi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)