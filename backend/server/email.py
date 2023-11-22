from flask import Blueprint, request, jsonify
import sqlite3
import os
from datetime import datetime

email_bp = Blueprint('email', __name__)

@email_bp.route('/email_rel', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')


    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    # SQLite 데이터베이스 설정 변경
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 새 댓글 추가
    cursor.execute("")

    # 변경사항 저장
    conn.commit()

    # 연결 종료
    conn.close()

    return jsonify('Email successfully', 200)