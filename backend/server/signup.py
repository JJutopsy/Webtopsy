from flask import Blueprint, request, jsonify
import bcrypt
from .db import get_db

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname')

    if not username or not email or not password:
        return jsonify({'message': '필수 필드를 모두 입력해주세요.', 'status': 400}), 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    conn, cursor = get_db()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return jsonify({'message': '이미 계정이 존재합니다.', 'status': 202}), 202

    cursor.execute('INSERT INTO users (username, email, password, salt, nickname) VALUES (?, ?, ?, ?, ?)',
                   (username, email, hashed_password, salt, nickname))
    conn.commit()
    conn.close()

    return jsonify({'message': '회원가입 성공', 'status': 200}), 200
