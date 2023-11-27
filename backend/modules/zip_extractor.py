import io
import zipfile
import logging
import sqlite3
import os
from . import parsing
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 원하는 확장자 목록
desired_extensions = [
    '.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt', '.zip'
]

# ZIP 스트림 처리 함수
def process_zip_stream(zip_stream, conn):
    with zipfile.ZipFile(zip_stream) as zipf:
        for info in zipf.infolist():
            if info.is_dir():
                continue

            file_name = info.filename
            corrected_file_name = file_name.encode('cp437').decode('euc-kr', 'ignore')
            ext = os.path.splitext(corrected_file_name)[1].lower()

            logging.info(f"Checking file: {corrected_file_name} with extension {ext}")

            if ext in desired_extensions:
                with zipf.open(file_name) as file:
                    file_data = file.read()
                    m_time = a_time = c_time = datetime(*info.date_time)
                    file_text = parsing.extract_text(file_data, ext)
                    hash_value = parsing.calculate_hash(file_data)
                    blob_data = sqlite3.Binary(file_data)
                    file_info = (corrected_file_name, hash_value, file_text, m_time.strftime("%Y-%m-%d %H:%M:%S"),
                                 a_time.strftime("%Y-%m-%d %H:%M:%S"), c_time.strftime("%Y-%m-%d %H:%M:%S"))

                    parsing.save_metadata_and_blob_to_db(conn, file_info, blob_data)

            elif ext == '.zip':
                inner_zip_data = zipf.read(file_name)
                process_zip_stream(io.BytesIO(inner_zip_data), conn)

# ZIP 파일 처리 함수
def process_zip_file(zip_filepath, case_id):
    # 해당 케이스 ID에 대응하는 파싱 결과 데이터베이스에 연결
    parsing_db_path = get_parsing_db_path(case_id)
    if not parsing_db_path:
        logging.error(f"Error: Could not find parsing DB path for case ID {case_id}")
        return

    conn = sqlite3.connect(parsing_db_path)  # 수정된 데이터베이스 연결
    logging.info(f"Connected to parsing database: {parsing_db_path}")
    try:
        with open(zip_filepath, 'rb') as file:
            process_zip_stream(io.BytesIO(file.read()), conn)
        logging.info(f"Completed processing {zip_filepath}")

    except Exception as e:
        logging.error(f"An error occurred while processing {zip_filepath}: {e}")

    finally:
        conn.close()

# 메인 실행
def process_zip(zip_filepath, case_id):  # zip_filepaths와 case_id를 매개변수로 받음
    process_zip_file(zip_filepath, case_id)

# get_parsing_db_path 함수 정의 (casedb에서 parsingDBpath 값을 조회)
def get_parsing_db_path(case_id):
    try:
        casedb_conn = sqlite3.connect('casedb.sqlite')
        cursor = casedb_conn.cursor()
        cursor.execute("SELECT parsingDBpath FROM cases WHERE parsingDBpath = ?", (case_id,))
        result = cursor.fetchone()
        casedb_conn.close()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        return None