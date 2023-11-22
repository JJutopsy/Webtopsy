from flask import Blueprint, request, jsonify
import sqlite3
import os
from datetime import datetime
from modules.eml_throw import EmailSearcher

email_bp = Blueprint('email', __name__)

@email_bp.route('/email_rel', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')
    eml_person = data.get('eml_person')
    related_person = data.get('related_person')

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
    
    email_searcher = EmailSearcher(db_path, eml_person, related_person)
    result = email_searcher.sort_and_print_related_emails()

    # return jsonify('Email successfully', 200)
    return jsonify({'result': result})