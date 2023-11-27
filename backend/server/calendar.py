from flask import Blueprint, request, jsonify
import os
import sqlite3

calendar_bp = Blueprint('calendar', __name__)

def get_document_fullpath(casename, document_name):
    db_path = os.path.join('cases', casename, 'parsing.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT file_path FROM your_table_name WHERE name = ?", (document_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    else:
        return None

def analyze_usnjrnl(e01_path, document_fullpath):
    # E01 파일 처리
    ewf_handle = libewf.handle()
    ewf_handle.open([e01_path])
    img_info = EwfImgInfo(ewf_handle)
    fs_info = pytsk3.FS_Info(img_info)
    
    # $UsnJrnl 파일 처리
    usn_jrnl_file_info = fs_info.open("/$Extend/$UsnJrnl")
    usn_jrnl_file_content = usn_jrnl_file_info.read_random(0, usn_jrnl_file_info.info.meta.size)

    print("Analyzing $USN J...")

@calendar_bp.route('/calendar', methods=['POST'])
def calendar_route():
    data = request.json
    
    if 'casedata' not in data or not data['casedata']:
        return jsonify({"error": "casedata is required"}), 400
    
    e01_path = data['casedata']
    
    if 'document_name' not in data or not data['document_name']:
        return jsonify({"error": "document_name is required"}), 400
    
    document_name = data['document_name']
    casename = data['casename']
    
    document_fullpath = get_document_fullpath(casename, document_name)
    if document_fullpath is None:
        return jsonify({"error": "Document not found in database"}), 404
    
    analyze_usnjrnl(e01_path, document_fullpath)
    
    return jsonify({"message": "Analysis started and will be reflected in the calendar view"})
