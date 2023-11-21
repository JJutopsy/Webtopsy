from flask import Blueprint, jsonify, request
import os

files_bp = Blueprint('files', __name__)

SUPPORTED_EXTENSIONS = ['E01', '001','dd','zip']
@files_bp.route('/files', methods=['POST'])
def list_files():
    path = request.json['path']
    print(path)
    
    try:
        files = os.listdir(path)
        file_data = []
        for file in files:
            
            file_path = os.path.join(path, file) 
            if os.path.isdir(file_path) or file_path.split(".")[-1] in SUPPORTED_EXTENSIONS:
                file_data.append({
                    'name': file,
                    'isDirectory': os.path.isdir(file_path)
                })
        return jsonify({'files': file_data})
    except Exception as e:
        return jsonify({'error': str(e)})
