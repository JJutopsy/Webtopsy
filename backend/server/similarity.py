from flask import Flask, request, jsonify, Blueprint
import sqlite3
import os
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET


similarity_bp = Blueprint('similarity', __name__)

@similarity_bp.route('/similarity', methods=['POST'])   
def similarity_analysis():
    data = request.json
    db_path = data['parsingDBpath']
    key_document_id = data['key_document_id']

    with sqlite3.connect(db_path) as conn:
        # 메타데이터 처리 및 해시 계산
        process_files(conn)
        # 유사한 미디어 파일이 포함된 문서 찾기
        similar_media = find_similar_media(conn, key_document_id)
        
        # 완전히 동일한 문서 찾기
        identical_documents = find_identical_documents(conn, key_document_id)

        # 메타데이터가 유사한 문서 찾기 (구현 필요)
        #similar_metadata_docs = find_similar_metadata_documents(conn, key_document_id)

    result = {
        "identical_documents": identical_documents,
        "similar_media": similar_media,
        #"similar_metadata_documents": similar_metadata_docs
    }

    return jsonify(result)

# OOXML 파일이 맞는지 확인하는 함수
def is_ooxml(filename):
    ooxml_extensions = ['.docx', '.xlsx', '.pptx']
    _, extension = os.path.splitext(filename)
    return extension in ooxml_extensions

# OOXML 파일에서 메타데이터를 추출하는 함수
def parse_metadata(blob_data, xml_file):
    with ZipFile(BytesIO(blob_data), 'r') as zip:
        with zip.open(xml_file) as xml:
            tree = ET.parse(xml)
            root = tree.getroot()
            metadata = {child.tag.split('}')[-1]: child.text for child in root}
            return metadata

# 데이터베이스에 메타데이터를 저장하는 함수
def save_metadata(conn, filename, metadata):
    cursor = conn.cursor()
    # 이미 생성된 documentmetadata 테이블의 현재 컬럼을 확인
    cursor.execute("PRAGMA table_info(documentmetadata);")
    existing_columns = {info[1] for info in cursor.fetchall()}

    # 새로운 메타데이터 키에 대해 필요한 경우 컬럼 추가
    for key in metadata.keys():
        if key not in existing_columns:
            cursor.execute(f'ALTER TABLE documentmetadata ADD COLUMN "{key}" TEXT;')
            conn.commit()

    # 기존에 해당 파일명으로 된 레코드가 있는지 확인
    cursor.execute("SELECT * FROM documentmetadata WHERE filename = ?", (filename,))
    row = cursor.fetchone()

    # 레코드가 없으면 새로운 레코드를 삽입
    if row is None:
        columns = '", "'.join(metadata.keys())
        placeholders = ', '.join('?' * len(metadata))
        sql = f'INSERT INTO documentmetadata ("filename", "{columns}") VALUES (?, {placeholders})'
        values = [filename] + list(metadata.values())
        cursor.execute(sql, values)
        conn.commit()
    else:
        # 레코드가 있으면 새로운 메타데이터 값으로 업데이트
        for key, value in metadata.items():
            if row[key] is None:
                sql = f'UPDATE documentmetadata SET "{key}" = ? WHERE filename = ?'
                cursor.execute(sql, (value, filename))
                conn.commit()

# OOXML 파일의 메타데이터를 처리하는 함수
def process_files(conn):
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, blob_data FROM files")
    rows = cursor.fetchall()
    for row in rows:
        file_path, blob_data = row['file_path'], row['blob_data']
        if is_ooxml(file_path):
            for xml_file in ['docProps/app.xml', 'docProps/core.xml']:
                metadata = parse_metadata(blob_data, xml_file)
                save_metadata(conn, file_path, metadata)

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