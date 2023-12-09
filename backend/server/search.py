from flask import Flask, Blueprint, request, jsonify
import sqlite3
import os
import re
import sys
from dotenv import load_dotenv

search_bp = Blueprint('search', __name__)

def highlight_keywords(text, keyword):
    highlighted = re.sub(f'({keyword})', r'<b>\1</b>', text, flags=re.IGNORECASE)
    return highlighted

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
            result_list.append({'id': row['id'], 'file_path': row['file_path'], 'plain_text': row['plain_text'], 'tag':row['tag'], 'NNP':row['NNP'], 'm_time':row['m_time'],'a_time':row['a_time'],'c_time':row['c_time']})

    return jsonify(result_list)

@search_bp.route('/keyword/email', methods=['POST'])
def search_Email_keyword():
    load_dotenv()

    data = request.get_json()
    parsingDBpath = data.get('parsingDBpath')
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
            result_list.append({'subject': row['subject'], 'date': row['date'], 'sender':row['sender'], 'receiver':row['receiver'], 'body':row['body']})

    return jsonify(result_list)