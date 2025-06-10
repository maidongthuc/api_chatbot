from flask import Flask, request, jsonify
from db_connection import connect_to_database
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
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)