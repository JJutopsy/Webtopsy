from flask import Blueprint, request, jsonify
import os
from modules.nnp_extractor import NERExtractor

nnp_bp = Blueprint('nnp', __name__)

@nnp_bp.route('/nnp_rel', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')
    

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404
    
    nnp = NERExtractor(db_path)
    nnp.process_texts()
    nnp.process_texts_eml()
    nnp.process_texts_emlAttachments()
    nnp.process_texts_pstAttachments()

    return jsonify('nnp successfully', 200)