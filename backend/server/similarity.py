from flask import Flask, request, jsonify, Blueprint
import sqlite3
import os
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from modules import total_similar


similarity_bp = Blueprint('similarity', __name__)

@similarity_bp.route('/similarity', methods=['POST'])   
def similarity_analysis():
    data = request.json
    db_path = data['parsingDBpath']
    key_document_id = data['key_document_id']

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        # 유사한 미디어 파일이 포함된 문서 찾기
        similar_media = find_similar_media(conn, key_document_id)
        
        # 완전히 동일한 문서 찾기
        identical_documents = find_identical_documents(conn, key_document_id)

        # 여러요소가 일치하는지 종합적인 문서 찾기 (평문,태그,메타데이터,미디어파일 해쉬값)
        
    similar_information_docs = total_similar.calculate_final_similarity(db_path, key_document_id)
    result = {
        "identical_documents": identical_documents,
        "similar_media": similar_media,
        "similar_information_docs": similar_information_docs
    }

    return jsonify(result)

def find_similar_media(conn, key_document_id):
    similar_documents = {}
    cursor = conn.cursor()

    # key_document_id에 해당하는 미디어 파일의 해시값과 총 개수를 가져옵니다.
    cursor.execute("SELECT SHA256Hash FROM MediaFiles WHERE DocumentID = ?", (key_document_id,))
    key_files_hashes = {row['SHA256Hash'] for row in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) FROM MediaFiles WHERE DocumentID = ?", (key_document_id,))
    key_media_count = cursor.fetchone()[0]

    # 모든 문서의 미디어 파일 수를 계산합니다.
    cursor.execute("SELECT DocumentID, COUNT(*) as TotalCount FROM MediaFiles GROUP BY DocumentID")
    total_media_count = {row['DocumentID']: row['TotalCount'] for row in cursor.fetchall()}

    # key_document_id를 제외한 모든 미디어 파일의 해시값과 원본 파일 이름을 가져옵니다.
    cursor.execute("SELECT DocumentID, SHA256Hash, SourceFileName FROM MediaFiles WHERE DocumentID != ?", (key_document_id,))
    all_other_files = cursor.fetchall()

    for row in all_other_files:
        doc_id = row['DocumentID']
        if row['SHA256Hash'] in key_files_hashes:
            if doc_id not in similar_documents:
                similar_documents[doc_id] = {'matched_count': 0, 'files': set()}
            similar_documents[doc_id]['matched_count'] += 1
            similar_documents[doc_id]['files'].add(row['SourceFileName'])

    # 결과를 정리하여 리턴합니다.
    result = []
    for doc_id, info in similar_documents.items():
        file_names_str = ", ".join(info['files'])  # 파일 이름 목록을 문자열로 변환
        match_ratio = f"{info['matched_count']}/{key_media_count}"  # 일치 비율 계산
        target_media_count = total_media_count.get(doc_id, 0)  # 대상 파일 미디어 전체 개수
        result.append({
            'DocumentID': doc_id,
            'TargetMediaCount': target_media_count,
            'SourceFileNames': file_names_str,
            'MatchRatio': match_ratio
            
        })

    return result
    
# 완전히 동일한 해시값을 가져와서 문서를 찾는 함수
def find_identical_documents(conn, key_document_id):
    identical_documents = []
    cursor = conn.cursor()

    # key_document_id에 해당하는 파일의 해시값 찾기
    cursor.execute("SELECT hash_value FROM files WHERE id = ?", (key_document_id,))
    row = cursor.fetchone()
    if not row:
        return identical_documents  # 해당 문서가 없는 경우 빈 리스트 반환

    key_hash = row['hash_value']

    # 같은 해시값을 가진 다른 파일들 찾기
    cursor.execute("SELECT id, file_path FROM files WHERE hash_value = ? AND id != ?", (key_hash, key_document_id))
    for row in cursor.fetchall():
        file_id, file_path = row['id'], row['file_path']
        identical_documents.append({'id': file_id, 'file_path': file_path})

    return identical_documents