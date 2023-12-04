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
    print("!!",parsingDBpath)
    keyword = data.get('keyword')

    if not os.path.exists(parsingDBpath):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    conn = sqlite3.connect(parsingDBpath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE file_path LIKE ? OR plain_text LIKE ?"
    results = cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%')).fetchall()
    print("이것은 리절트 값입니다:", results)

    conn.close()

    if not results:
        print("이것은 리절트 값입니다:", results)
        return '검색 결과가 없습니다.', 404

    result_list = []
    for row in results:
        highlighted_content = highlight_keywords(row['plain_text'], keyword)
        result_list.append({'id': row['id'], 'file_path': row['file_path'], 'plain_text': row['plain_text'], 'tag':row['tag']})

    return jsonify(result_list)

    result_list = []
    for row in results:
        highlighted_content = highlight_keywords(row['content'], keyword)
        result_list.append({'id': row['id'], 'name': row['name'], 'content': highlighted_content})

    return jsonify(result_list)