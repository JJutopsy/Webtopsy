from flask import Blueprint, request, jsonify
import sqlite3
import os
from datetime import datetime

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comment', methods=['POST'])
def post_comment():
    data = request.get_json()
    post_id = data.get('post_id')
    username = data.get('username')
    context = data.get('context')
    db_path = data.get('db_path')
    type = data.get('type')

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    # SQLite 데이터베이스 설정 변경
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    #cursor.execute("DROP TABLE IF EXISTS comments")
    
    # 새 댓글 추가
    cursor.execute("INSERT INTO comments (post_id, username, context, type) VALUES (?, ?, ?, ?)", (post_id, username, context, type))

    # 변경사항 저장
    conn.commit()

    # 연결 종료
    conn.close()

    return jsonify('Comment added successfully', 200)

@comment_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    data = request.get_json()
    db_path = data.get('db_path')

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    # SQLite 데이터베이스 설정 변경
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 댓글 삭제
    cursor.execute("DELETE FROM comments WHERE id=?", (comment_id,))

    # 변경사항 저장
    conn.commit()

    # 연결 종료
    conn.close()

    return jsonify('Comment deleted successfully', 200)

@comment_bp.route('/comments/<int:post_id>', methods=['POST'])
def get_comments(post_id):
    data = request.get_json()
    db_path = data.get('db_path')

    if not os.path.exists(db_path):
        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    # SQLite 데이터베이스 설정 변경
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 댓글 불러오기
    cursor.execute("SELECT * FROM comments WHERE post_id=?", (post_id,))
    comments = cursor.fetchall()
    result_list = []
    for row in comments:
        result_list.append({'id': row['id'], 'post_id': row['post_id'], 'username': row['username'], 'context':row['context'], 
                            'created_at':row['created_at'],'type':row['type'] })
    # 연결 종료
    conn.close()

    return jsonify(result_list)

@comment_bp.route('/recent_comments', methods=['POST'])
def get_recent_comments():
    data = request.get_json()
    db_path = data.get('db_path')
    print(db_path)
    if not os.path.exists(db_path):

        return '데이터베이스 파일을 찾을 수 없습니다.', 404

    # SQLite 데이터베이스 설정 변경
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 최근 댓글 10개 불러오기
    cursor.execute("SELECT * FROM comments ORDER BY created_at DESC LIMIT 10")
    comments = cursor.fetchall()
    result_list = []
    for row in comments:
        result_list.append({'id': row['id'], 'post_id': row['post_id'], 'username': row['username'], 'context':row['context'], 
                            'created_at':row['created_at'],'type':row['type'] })

    # 연결 종료
    conn.close()
    print(result_list)
    return jsonify(result_list)