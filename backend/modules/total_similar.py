import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os


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
    keyfile_tags_row = cursor.fetchone()

    if keyfile_tags_row is None or keyfile_tags_row[0] is None:
        keyfile_tags = set()
    else:
        keyfile_tags = set(keyfile_tags_row[0].split(','))

    # 다른 파일들의 태그와 ID 가져오기
    cursor.execute("SELECT id, tag FROM files WHERE id != ?", (key_file_id,))
    other_files_tags = cursor.fetchall()

    # 일치율 계산
    matching_ratios = []
    for file_id, tags in other_files_tags:
        if tags is None:
            tags = ''
        tags_set = set(tags.split(','))
        matching_count = len(tags_set & keyfile_tags)
        total_tags = len(keyfile_tags)

        if total_tags > 0:
            matching_ratio = (matching_count / total_tags) * 100
        else:
            matching_ratio = 0

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
    columns = ["creator", "created", "AppVersion", "Application", "Company", "Template"]
    keyfile_metadata = []
    for column in columns:
        try:
            cursor.execute(f"SELECT {column} FROM documentmetadata WHERE filename = ?", (keyfile_name,))
            result = cursor.fetchone()
            if result is not None:
                keyfile_metadata.append(result[0])
            else:
             keyfile_metadata.append(None)
        except sqlite3.OperationalError:
            keyfile_metadata.append(None)

    # keyfile이 아닌 다른 모든 파일들의 지정된 컬럼들에 대한 메타데이터를 가져옴
    other_files_metadata = []
    cursor.execute("SELECT id FROM documentmetadata WHERE filename != ?", (keyfile_name,))
    other_files_ids = cursor.fetchall()
    for file_id_tuple in other_files_ids:
        file_id = file_id_tuple[0]  # file_id를 튜플에서 추출
        file_metadata = [file_id]
        for column in columns:
            try:
                cursor.execute(f"SELECT {column} FROM documentmetadata WHERE id = ?", (file_id,))  # file_id를 직접 사용
                file_metadata.append(cursor.fetchone()[0])
            except sqlite3.OperationalError:
                file_metadata.append(None)
        other_files_metadata.append(tuple(file_metadata))
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

    # 'MediaFiles' 테이블에서 'SourceFileName'이 파일명과 일치하는 레코드의 해시 값 가져오기
    c.execute(f"SELECT SHA256Hash FROM MediaFiles WHERE DocumentID='{key_file_id}'")
    key_file_hashes = [row[0] for row in c.fetchall()]

    # 키 파일의 해시가 없는 경우, 빈 리스트 반환
    if not key_file_hashes:
        return []

    # 키 파일을 제외한 각 파일에 대해 일치율 계산
    c.execute(f"SELECT DISTINCT id, file_path FROM files WHERE id<>{key_file_id}")
    other_files = c.fetchall()

    media_match_rates = []
    for file_id, file_path in other_files:
        c.execute(f"SELECT SHA256Hash FROM MediaFiles WHERE DocumentID='{file_id}'")
        other_file_hashes = [row[0] for row in c.fetchall()]

        # 일치하는 해시 값의 개수 계산
        matching_hashes = set(key_file_hashes) & set(other_file_hashes)
        match_rate = (len(matching_hashes) / len(key_file_hashes)) * 100 if key_file_hashes else 0

        media_match_rates.append((file_id, match_rate))

    return media_match_rates

def calculate_final_similarity(db_path, key_file_id):
    # 최종 결과를 담을 리스트를 초기화합니다.
    final_ratios = []

    # SQLite DB 연결을 초기화합니다.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 각 파일별 일치율을 저장할 임시 딕셔너리를 초기화합니다.
    temp_ratios = {}

    # 모든 일치율 리스트를 순회합니다.
    for ratio_weight, ratios in zip([0.20, 0.40, 0.15, 0.25], 
         [calculate_cosine_similarity(db_path, key_file_id), calculate_tag_matching_ratio(db_path, key_file_id),
          calculate_metadata_matching_ratio(db_path, key_file_id), calculate_media_match_rate(db_path, key_file_id)]):
        for file_id, ratio in ratios:
            # 파일별 일치율을 비율에 맞게 합칩니다.
            if file_id in temp_ratios:
                temp_ratios[file_id]['ratio'] += ratio * ratio_weight
            else:
                # documentmetadata 테이블에서 파일명을 찾습니다.
                cursor.execute("SELECT filename FROM documentmetadata WHERE file_id=?", (file_id,))
                row = cursor.fetchone()
                if row:  # 파일명이 존재하는 경우에만 결과에 추가합니다.
                    temp_ratios[file_id] = {'file_id': file_id, 'filename': row[0], 'ratio': ratio * ratio_weight}

    # 파일별 일치율을 계산하여 결과에 추가합니다.
    for file_id, data in temp_ratios.items():
        data['ratio'] = round(data['ratio'], 2)  # 유사도 점수를 소수점 두 자리까지 반올림합니다.
        final_ratios.append(data)

    conn.close()

    return final_ratios