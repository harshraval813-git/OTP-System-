from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app) # Yeh frontend ko backend se connect karne ke liye zaroori hai

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # XAMPP mein default blank hota hai
        database="otp_project"
    )

# 1st API Route: OTP Generate aur Send karne ke liye
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    # 6-digit random number
    otp = str(random.randint(100000, 999999))
    # Current time se 5 minute aage ki expiry
    expiry_time = datetime.now() + timedelta(minutes=5)
    
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # Database mein entry karna
        cursor.execute("INSERT INTO otp_logs (email, otp, expiry_time) VALUES (%s, %s, %s)", (email, otp, expiry_time))
        db.commit()
        cursor.close()
        db.close()
        
        # Testing ke liye OTP terminal me print kar rahe hain (interview me demonstrate karne ke liye best)
        print(f"\n======================================")
        print(f"SUCCESS: OTP for {email} is {otp}")
        print(f"======================================\n")
        
        return jsonify({"message": "OTP sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2nd API Route: OTP Verify karne ke liye
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    user_otp = data.get('otp')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # DB me check karna ki OTP match ho raha hai ya nahi
    cursor.execute("SELECT * FROM otp_logs WHERE email = %s AND otp = %s AND is_verified = FALSE ORDER BY id DESC LIMIT 1", (email, user_otp))
    record = cursor.fetchone()
    
    if record:
        # Check expiry time
        if record['expiry_time'] > datetime.now():
            # Success! is_verified ko True kar do
            cursor.execute("UPDATE otp_logs SET is_verified = TRUE WHERE id = %s", (record['id'],))
            db.commit()
            return jsonify({"message": "Login Successful! Welcome."}), 200
        else:
            return jsonify({"error": "OTP Expired."}), 400
    else:
        return jsonify({"error": "Invalid OTP."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)