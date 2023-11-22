from flask import Blueprint, request, jsonify
import os
from modules.emlperson_extractor import EmlPersonUpdater

emailperson_bp = Blueprint('emailPerson', __name__)

@emailperson_bp.route('/email_emlperson', methods=['POST'])
def email_relation():
    data = request.get_json()
    db_path = data.get('db_path')
    

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404
    
    eml_person_updater = EmlPersonUpdater(db_path)
    eml_person_updater.update_eml_person_table()

    return jsonify('EmailPerson successfully', 200)