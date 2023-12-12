from flask import Flask, Blueprint, request, jsonify
import sqlite3
import os
import re
import sys
from dotenv import load_dotenv
from datetime import datetime
search_bp = Blueprint('search', __name__)

def highlight_keywords(text, keyword):
    highlighted = re.sub(f'({keyword})', r'<b>\1</b>', text, flags=re.IGNORECASE)
    return highlighted

@search_bp.route('/keyword/<int:file_id>', methods=['POST'])
def search_id(file_id):
    load_dotenv()

    data = request.get_json()
    parsingDBpath = os.environ.get("REACT_APP_HOME") + "/" + data.get('db_path')

    if not os.path.exists(parsingDBpath):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    conn = sqlite3.connect(parsingDBpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE id = ?"
    result = cursor.execute(query, (file_id,)).fetchone()

    conn.close()

    if not result:
        return '검색 결과가 없습니다.', 404
    result_dict = {}
    row = dict(result)
    if row['tag'] and row['NNP']:
        m_time = datetime.strptime(row['m_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")
        a_time = datetime.strptime(row['a_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")
        c_time = datetime.strptime(row['c_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")

        result_dict = {
        'id': row['id'],
        'file_path': row['file_path'],
        'owner': row['owner'],
        'plain_text': row['plain_text'],
        'hash': row['hash_value'],
        'tag': row['tag'],
        'NNP': row['NNP'],
        'm_time': m_time,
        'a_time': a_time,
        'c_time': c_time
            }
        return jsonify(result_dict)
    return 'TAG 또는 NNP가 없습니다.',400
@search_bp.route('/keyword', methods=['POST'])
def search_keyword():
    load_dotenv()

    data = request.get_json()
    parsingDBpath = os.environ.get("REACT_APP_HOME")+"/"+data.get('parsingDBpath')
    keyword = data.get('keyword')

    if not os.path.exists(parsingDBpath):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    conn = sqlite3.connect(parsingDBpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE file_path LIKE ? OR plain_text LIKE ?"
    results = cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()


    conn.close()

    if not results:
 
        return '검색 결과가 없습니다.', 404

    
    result_list = []
    for row in results:
        if row['tag'] and row['NNP']:
            m_time = datetime.strptime(row['m_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")
            a_time = datetime.strptime(row['a_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")
            c_time = datetime.strptime(row['c_time'], "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M")

            result_list.append({'id': row['id'], 'file_path': row['file_path'], 'owner':row['owner'], 'plain_text': row['plain_text'], 'hash':row['hash_value'], 'tag':row['tag'], 'NNP':row['NNP'], 'm_time':m_time,'a_time':a_time,'c_time':c_time})
    
    return jsonify(result_list)


@search_bp.route('/keyword/email', methods=['POST'])
def search_Email_keyword():
    load_dotenv()

    data = request.get_json()
    parsingDBpath = os.environ.get("REACT_APP_HOME")+"/"+data.get('parsingDBpath')
    keyword = data.get('keyword')

    if not os.path.exists(parsingDBpath):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    conn = sqlite3.connect(parsingDBpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM emlEmails WHERE subject LIKE ? OR body LIKE ?"
    results = cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()

    conn.close()
    if not results:
 
        return '검색 결과가 없습니다.', 404
    result_list = []
    for row in results:
            result_list.append({'subject': row['subject'], 'date': row['date'], 'sender':row['sender'], 'receiver':row['receiver'], 'body':row['body'], 'tag':row['tag'], 'NNP':row['NNP'], 'file_path':row['save_location'], 'id':row['id']})

    return jsonify(result_list)
