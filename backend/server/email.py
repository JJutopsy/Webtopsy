from flask import Blueprint, request, jsonify
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
    try:
        email_searcher = EmailSearcher(db_path, eml_person, related_person)
        result = email_searcher.sort_and_print_related_emails()

        # return jsonify('Email successfully', 200)
        return jsonify({'result': result})
    
    except Exception as e:
        return jsonify({'error': str(e)})