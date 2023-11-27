from flask import Blueprint, request, jsonify
import os
from modules.tag_extractor import KeywordExtractor

tag_bp = Blueprint('tag', __name__)

@tag_bp.route('/tag_rel', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')
    

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404
    
    try:
        tag = KeywordExtractor(db_path)
        tag.extract_keywords()
        tag.extract_keywords_eml()
        tag.extract_keywords_emlAttachments()
        tag.extract_keywords_pstAttachments()
    
        return jsonify('tagmatch successfully', 200)
    
    except Exception as e:
        return jsonify({'error': str(e)})