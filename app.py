import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Database Configuration
# Jab aap Aiven ya kisi cloud DB par jayenge, toh ye details badal jayengi
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'otp_project'),
        port=os.getenv('DB_PORT', '3306')
    )

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    otp = str(random.randint(100000, 999999))
    expiry_time = datetime.now() + timedelta(minutes=5)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO otp_logs (email, otp, expiry_time) VALUES (%s, %s, %s)"
        cursor.execute(query, (email, otp, expiry_time))
        db.commit()
        cursor.close()
        db.close()
        print(f"SUCCESS: OTP for {email} is {otp}") # Terminal mein check karne ke liye
        return jsonify({"message": "OTP generated successfully!", "otp": otp}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp_provided = data.get('otp')

    try:
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT otp, expiry_time FROM otp_logs WHERE email = %s AND is_verified = FALSE ORDER BY id DESC LIMIT 1"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result:
            db_otp, expiry = result
            if datetime.now() < expiry and db_otp == otp_provided:
                update_query = "UPDATE otp_logs SET is_verified = TRUE WHERE email = %s AND otp = %s"
                cursor.execute(update_query, (email, otp_provided))
                db.commit()
                return jsonify({"message": "Login Successful!"}), 200
            else:
                return jsonify({"message": "Invalid or Expired OTP"}), 400
        else:
            return jsonify({"message": "No OTP found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

if __name__ == '__main__':
    # Render ke liye host '0.0.0.0' aur port 10000 set karna zaroori hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)