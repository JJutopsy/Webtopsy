from flask import Blueprint, request, jsonify
import os
from modules.file_ismatch import FileProcessor

ismatch_bp = Blueprint('fileismatch', __name__)

@ismatch_bp.route('/file_ismatch', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')
    

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404
    
    try:
        ismatch = FileProcessor(db_path)
        ismatch.process_file()
        ismatch.process_file_emlAttachments()
        ismatch.process_file_pstAttachments()

        return jsonify('ismatch successfully', 200)
    except Exception as e:
        return jsonify({'error': str(e)})