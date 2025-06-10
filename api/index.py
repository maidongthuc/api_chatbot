import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from src.db_connection import connect_to_database
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
# Route cho trang chủ
@app.route('/')
def home():
    return 'Chào mừng bạn đến với Flask!'

# Route có tham số tên, hiển thị lời chào cá nhân hóa
@app.route('/hello')
def greet():
    conn = connect_to_database()
    if conn:
        conn.close()  # Close the connection after testing
        return "Database connection successful!"
    else:
        return "Database connection failed!", 500

@app.route('/history_chat', methods=['POST'])
def history_chat():
    # Check if the request's Content-Type is application/json
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    # Parse JSON data from the request
    conn = connect_to_database()
    data = request.get_json()
    user_msg = data.get('user')
    assistant_msg = data.get('assistant')
    user_id = data.get('user_id')
    if conn:
        cursor = conn.cursor()
        # Insert the user and assistant messages into the database
        sql = "INSERT INTO history_chatbot (user, assistant, id_user) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_msg, assistant_msg, user_id))

        conn.commit()
        cursor.close()
        conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    # Log messages to the console (optional)
    print(f'User: {user_msg}')
    print(f'Assistant: {assistant_msg}')

    # Return a response
    return jsonify({
        "received": {
            "user": user_msg,
            "assistant": assistant_msg
        }
    })


@app.route('/login', methods=['POST'])
def login():
    # Kiểm tra Content-Type của request
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    # Lấy dữ liệu từ request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Kiểm tra các trường bắt buộc
    if not username or not password:
        return jsonify({"error": "Missing required fields: username or password"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Kiểm tra username là email hoặc phone
            sql = """
                SELECT password, id FROM users 
                WHERE email = %s OR phone = %s
            """
            cursor.execute(sql, (username, username))
            result = cursor.fetchone()

            if result:
                # So sánh password
                stored_password = result[0]
                user_id = result[1]
                if stored_password == password:
                    return jsonify({"message": "Login successful", "user_id": user_id}), 200
                else:
                    return jsonify({"error": "Invalid password"}), 401
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to process login"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/get_profile', methods=['GET'])
def get_profile():
    # Lấy user_id từ query string
    user_id = request.args.get('user_id')

    # Kiểm tra nếu user_id không được cung cấp
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Truy vấn thông tin hồ sơ người dùng dựa trên user_id
            sql = """
                SELECT fullname, email, phone, gender, day_of_birth, 
                       month_of_birth, year_of_birth, height, weight, medical_history
                FROM users
                WHERE id = %s
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if result:
                # Định dạng dữ liệu trả về
                profile = {
                    "fullname": result[0],
                    "email": result[1],
                    "phone": result[2],
                    "gender": result[3],
                    "day_of_birth": result[4],
                    "month_of_birth": result[5],
                    "year_of_birth": result[6],
                    "height": result[7],
                    "weight": result[8],
                    "medical_history": result[9]
                }
                return jsonify({"message": "Profile retrieved successfully", "profile": profile}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to retrieve profile"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/history_chat', methods=['GET'])
def get_history_chat():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing conversation_id"}), 400

    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Truy vấn dữ liệu từ bảng history_chatbot
            sql = "SELECT user, assistant FROM history_chatbot WHERE id_user = %s ORDER BY time"
            cursor.execute(sql, (user_id))
            rows = cursor.fetchall()
            print(rows)  # Log kết quả ra console (tuỳ chọn)

            # Chuyển đổi dữ liệu thành định dạng mong muốn
            messages = []
            for row in rows:
                user_message = {"role": "user", "content": row[0]} if row[0] else None
                assistant_message = {"role": "assistant", "content": row[1]} if row[1] else None
                if user_message:
                    messages.append(user_message)
                if assistant_message:
                    messages.append(assistant_message)

        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Database query failed"}), 500
        finally:
            cursor.close()
            conn.close()

        # Trả về danh sách các tin nhắn
        return jsonify(messages)
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/create_account', methods=['POST'])
def create_account():
    # Kiểm tra Content-Type của request
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    # Lấy dữ liệu từ request
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # Kiểm tra các trường bắt buộc
    if not email or not phone or not password:
        return jsonify({"error": "Missing required fields: email, phone, or password"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Thêm tài khoản mới vào bảng users
            sql = "INSERT INTO users (email, phone, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (email, phone, password))
            conn.commit()
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to create account"}), 500
        finally:
            cursor.close()
            conn.close()

        # Trả về phản hồi thành công
        return jsonify({"message": "Account created successfully"}), 201
    else:
        return jsonify({"error": "Database connection failed"}), 500
@app.route('/check_fullname', methods=['GET'])
def check_fullname():
    # Lấy user_id từ query string
    user_id = request.args.get('user_id')

    # Kiểm tra nếu user_id không được cung cấp
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Truy vấn fullname của user dựa trên user_id
            sql = "SELECT fullname FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if result:
                fullname = result[0]
                if fullname:
                    return jsonify({"message": "Fullname exists", "fullname": fullname}), 404
                else:
                    return jsonify({"message": "Fullname is null"}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to check fullname"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500    
@app.route('/update_user', methods=['POST'])
def update_user():
    # Kiểm tra Content-Type của request
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    # Lấy dữ liệu từ request
    data = request.get_json()
    user_id = data.get('user_id')
    fullname = data.get('fullname')
    gender = data.get('gender')
    day_of_birth = data.get('day_of_birth')
    month_of_birth = data.get('month_of_birth')
    year_of_birth = data.get('year_of_birth')
    height = data.get('height')
    weight = data.get('weight')
    medical_history = data.get('medical_history')

    print(user_id, fullname, gender, day_of_birth, month_of_birth, year_of_birth, height, weight, medical_history)  # Log dữ liệu nhận được (tuỳ chọn)
    # Kiểm tra các trường bắt buộc
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Cập nhật thông tin người dùng
            sql = """
                UPDATE users
                SET fullname = %s, gender = %s, day_of_birth = %s, 
                    month_of_birth = %s, year_of_birth = %s, 
                    height = %s, weight = %s, medical_history = %s
                WHERE id = %s
            """
            cursor.execute(sql, (fullname, gender, day_of_birth, month_of_birth, year_of_birth, height, weight, medical_history, user_id))
            conn.commit()

            # Kiểm tra xem có dòng nào được cập nhật không
            if cursor.rowcount > 0:
                return jsonify({"message": "User information updated successfully"}), 200
            else:
                return jsonify({"error": "User not found or no changes made"}), 404
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to update user information"}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/id_conversation', methods=['GET'])
def get_id_conversation():
    user_id = request.args.get('user_id')
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()  # Sử dụng con trỏ mặc định
            # Sử dụng DISTINCT để lấy các conversation_id không trùng lặp
            sql = "SELECT DISTINCT conversation_id FROM history_chatbot wHERE id_user = %s"
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            print(rows)  # Log kết quả ra console (tuỳ chọn)
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Database query failed"}), 500
        finally:
            cursor.close()
            conn.close()
        
        # Trả về danh sách các conversation_id
        return jsonify([row[0] for row in rows])
    else:
        return jsonify({"error": "Database connection failed"}), 500



@app.route('/save_vital_sign', methods=['GET'])
def save_vital_sign():
    # Lấy các tham số từ query string
    user_id = request.args.get('user_id')
    temp = request.args.get('temp')
    heart_rate = request.args.get('heart_rate')
    spo2 = request.args.get('spo2')
    sys = request.args.get('sys')
    dia = request.args.get('dia')

    # Kiểm tra nếu user_id không được cung cấp
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Thêm dấu thời gian hiện tại
            sql = """
                INSERT INTO vital_sign (user_id, temp, heartRate, spo2, sys, dia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, temp, heart_rate, spo2, sys, dia))
            conn.commit()
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Failed to save vital signs"}), 500
        finally:
            cursor.close()
            conn.close()

        # Trả về phản hồi thành công
        return jsonify({"message": "Vital signs saved successfully"}), 201
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/get_vital_sign', methods=['GET'])
def get_vital_sign():
    # Lấy user_id từ query string
    user_id = request.args.get('user_id')

    # Kiểm tra nếu user_id không được cung cấp
    if not user_id:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # Kết nối tới cơ sở dữ liệu
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Truy vấn các dấu hiệu sinh tồn của người dùng
            sql = """
                SELECT temp, heartRate, spo2, sys, dia, created_at 
                FROM vital_sign 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()

            # Chuyển đổi dữ liệu thành định dạng mong muốn
            vital_signs = []
            for row in rows:
                vital_signs.append({
                    "temp": row[0],
                    "heartRate": row[1],
                    "spo2": row[2],
                    "sys": row[3],
                    "dia": row[4],
                    "time": row[5].strftime('%Y-%m-%d %H:%M:%S')  # Định dạng thời gian
                })

        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Database query failed"}), 500
        finally:
            cursor.close()
            conn.close()

        # Trả về danh sách các dấu hiệu sinh tồn
        return jsonify(vital_signs)
    else:
        return jsonify({"error": "Database connection failed"}), 500
# Chạy ứng dụng nếu chạy trực tiếp file này
if __name__ == '__main__':
    app.run(debug=True, port=5000)
