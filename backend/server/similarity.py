from flask import Flask, request, jsonify, Blueprint
import sqlite3
import os
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


similarity_bp = Blueprint('similarity', __name__)

@similarity_bp.route('/similarity', methods=['POST'])   
def similarity_analysis():
    data = request.json
    db_path = data['parsingDBpath']
    key_document_id = data['key_document_id']

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_path FROM files WHERE id=?", (key_document_id,))
        rows = cursor.fetchall()
        
        # 키파일 ID가 files 테이블에 없으면 함수를 종료
        if not rows:
            return jsonify({"message": "key_document_id가 files 테이블에 존재하지 않습니다."})
        
        # 파일 경로의 마지막 부분이 ooxml 파일 확장자가 아니면 함수를 종료
        _, file_path = rows[0]
        if not file_path.lower().endswith(('.docx', '.xlsx', '.pptx')):
            return jsonify({"message": "지정된 파일은 ooxml 구조의 확장자를 가지고 있지 않습니다."})

        # 메타데이터 처리 및 해시 계산
        process_files(conn)
        
        # 유사한 미디어 파일이 포함된 문서 찾기
        similar_media = find_similar_media(conn, key_document_id)

        # 완전히 동일한 문서 찾기
        identical_documents = find_identical_documents(conn, key_document_id)

        # 여러요소(평문,태그,미디어,메타데이터)가 유사한 문서 찾기 
        final_similar_metadata_docs = calculate_final_similarity(conn, key_document_id)

    result = {
        "identical_documents": identical_documents,
        "similar_media": similar_media,
        "final_similar_metadata_documents": final_similar_metadata_docs
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



def calculate_cosine_similarity(db_path, key_file_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # keyfile의 plain_text 가져오기
    cursor.execute("SELECT plain_text FROM files WHERE id = ?", (key_file_id,))
    keyfile_text = cursor.fetchone()[0]

    # 다른 파일들의 plain_text 가져오기
    cursor.execute("SELECT id, plain_text FROM files WHERE id != ?", (key_file_id,))
    other_files = cursor.fetchall()

    other_files_text = [row[1] for row in other_files]

    # 텍스트를 벡터화
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([keyfile_text] + other_files_text)

    # 코사인 유사도 계산
    cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    # 결과에 대한 파일 ID와 유사도를 리스트 형태로 반환
    result = [(file[0], similarity) for file, similarity in zip(other_files, cosine_similarities)]

    return result



def calculate_tag_matching_ratio(db_path, key_file_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 키 파일의 태그 가져오기
    cursor.execute("SELECT tag FROM files WHERE id = ?", (key_file_id,))
    keyfile_tags = cursor.fetchone()[0].split(',')

    # 다른 파일들의 태그와 ID 가져오기
    cursor.execute("SELECT id, tag FROM files WHERE id != ?", (key_file_id,))
    other_files_tags = cursor.fetchall()

    # 일치율 계산
    matching_ratios = []
    for file_id, tags in other_files_tags:
        matching_count = sum([1 for tag in tags.split(',') if tag in keyfile_tags])
        matching_ratio = (matching_count / len(keyfile_tags)) * 100
        matching_ratios.append((file_id, matching_ratio))

    return matching_ratios



def calculate_metadata_matching_ratio(db_path, key_file_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # keyfile의 파일 경로를 가져옴
    cursor.execute("SELECT file_path FROM files WHERE id = ?", (key_file_id,))
    keyfile_path = cursor.fetchone()[0]
    keyfile_name = os.path.basename(keyfile_path)

    # keyfile의 지정된 컬럼들에 대한 메타데이터를 가져옴
    cursor.execute("SELECT creator, created, AppVersion, Application, Company, Template FROM documentmetadata WHERE filename = ?", (keyfile_name,))
    keyfile_metadata = cursor.fetchone()

    # keyfile이 아닌 다른 모든 파일들의 지정된 컬럼들에 대한 메타데이터를 가져옴
    cursor.execute("SELECT id, creator, created, AppVersion, Application, Company, Template FROM documentmetadata WHERE filename != ?", (keyfile_name,))
    other_files_metadata = cursor.fetchall()

    # 일치 비율을 계산함
    matching_ratios = []
    for metadata in other_files_metadata:
        matching_count = sum([1 for key_meta, other_meta in zip(keyfile_metadata, metadata[1:]) if key_meta == other_meta and key_meta is not None])
        matching_ratios.append((metadata[0], (matching_count / len(keyfile_metadata)) * 100))  # 일치 비율을 백분율로 표현

    return matching_ratios


def calculate_media_match_rate(db_path, key_file_id):
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 'files' 테이블에서 키 파일 ID에 해당하는 레코드의 파일 경로 가져오기
    c.execute(f"SELECT file_path FROM files WHERE id={key_file_id}")
    key_file_path = c.fetchone()[0]

    # 파일 경로에서 파일명 추출
    key_file_name = os.path.basename(key_file_path)

    # 'MediaFiles' 테이블에서 'SourceFileName'이 파일명과 일치하는 레코드의 해시 값 가져오기
    c.execute(f"SELECT SHA256Hash FROM MediaFiles WHERE SourceFileName='{key_file_name}'")
    key_file_hashes = [row[0] for row in c.fetchall()]

    # 키 파일을 제외한 각 파일에 대해 일치율 계산
    c.execute(f"SELECT DISTINCT id, file_path FROM files WHERE id<>{key_file_id}")
    other_files = c.fetchall()

    media_match_rates = []
    for file_id, file_path in other_files:
        file_name = os.path.basename(file_path)
        c.execute(f"SELECT SHA256Hash FROM MediaFiles WHERE SourceFileName='{file_name}'")
        other_file_hashes = [row[0] for row in c.fetchall()]

        # 일치하는 해시 값의 개수 계산
        matching_hashes = set(key_file_hashes) & set(other_file_hashes)
        match_rate = len(matching_hashes) / len(key_file_hashes) * 100

        media_match_rates.append((file_id, match_rate))

    return media_match_rates

def calculate_final_similarity(db_path, key_file_id):
    # 파일별 일치율을 담을 딕셔너리를 초기화합니다.
    final_ratios = {}

    # 모든 일치율 리스트를 순회합니다.
    for ratios in [calculate_cosine_similarity(db_path, key_file_id), calculate_tag_matching_ratio(db_path, key_file_id),
                    calculate_metadata_matching_ratio(db_path, key_file_id), calculate_media_match_rate(db_path, key_file_id)]:
        for file_id, ratio in ratios:
            # 파일별 일치율을 동일한 비율로 합칩니다.
            if file_id in final_ratios:
                final_ratios[file_id] += ratio
            else:
                final_ratios[file_id] = ratio

    # 파일별 일치율의 평균을 계산합니다.
    for file_id in final_ratios:
        final_ratios[file_id] /= 4

    return final_ratios