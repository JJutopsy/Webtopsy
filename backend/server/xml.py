from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from .db import get_db
from modules import xml_extractor

xml_bp = Blueprint('xml', __name__)

@xml_bp.route('/xml', methods=['POST'])
def xml_ext():
    print('1')
    data = request.get_json()
    db_path = data.get('db_path')
    xml_extractor.process_files(db_path)
    return jsonify('파싱 성공')