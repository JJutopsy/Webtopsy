from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from .db import get_db

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '사용자 이름과 패스워드를 입력해주세요.', 'status': 400}), 400

    conn, cursor = get_db()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # JWT 토큰 생성
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, 'your_secret_key', algorithm='HS256')

        return jsonify({'status': 200, 'result': {'token': token}}), 200
    else:
        return jsonify({'status': 201}), 201
