import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # .strip() ka use kiya hai taaki extra spaces delete ho jayein
    host = os.getenv('DB_HOST', '').strip()
    port = os.getenv('DB_PORT', '14706').strip()
    user = os.getenv('DB_USER', '').strip()
    password = os.getenv('DB_PASSWORD', '').strip()
    database = os.getenv('DB_NAME', '').strip()
    
    print(f"DEBUG: Connecting to Host: '{host}' on Port: {port}")
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)
    )

def init_db():
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                otp VARCHAR(6) NOT NULL,
                expiry_time DATETIME NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE
            )
        """)
        db.commit()
        cursor.close()
        db.close()
        print("TABLE CHECK: Table 'otp_logs' is ready!")
    except Exception as e:
        print(f"DATABASE ERROR during init: {e}")

@app.route('/')
def home():
    return "OTP Backend is Running with Cloud DB!"

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
    init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)