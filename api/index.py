from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 
# Route cho trang chủ
@app.route('/')
def home():
    return 'Chào mừng bạn đến với Flask!'
