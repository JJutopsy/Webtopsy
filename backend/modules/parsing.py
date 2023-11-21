import hashlib
import sqlite3
import time
from pathlib import Path
from io import BytesIO
from .ole_extractor import OLEExtractor
from .hwp_extractor import HWPExtractor
from .docx_extractor import DOCXExtractor
from .pptx_extractor import PPTXExtractor
from .xlsx_extractor import XLSXExtractor
from .eml_extractor import EmlExtractor
from .pst_extractor import PSTExtractor
from .pdf_extractor import PDFExtractor
import zipfile
import logging
import os
import tempfile

def read_file_with_different_encodings(file_data):
    encodings = ['utf-8', 'iso-8859-1', 'cp949']  
    for encoding in encodings:
        try:
            return file_data.decode(encoding).strip()
        except Exception:
            continue
    raise Exception("Unable to decode the file data with the provided encodings.")

def extract_text(file_data, ext):
    text = ""
    try:
        if ext in [".doc", ".ppt", ".xls"]:
            extractor = OLEExtractor(file_data)
            text = extractor.get_text()
        elif ext == ".docx":
            extractor = DOCXExtractor(file_data)
            text = extractor.get_text()
        elif ext == ".pptx":
            extractor = PPTXExtractor(file_data)
            text = extractor.get_text()
        elif ext == ".xlsx":
            extractor = XLSXExtractor(file_data)
            text = extractor.get_text()
        elif ext == ".hwp":
            extractor = HWPExtractor(file_data)
            text = extractor.get_text()
        elif ext == ".pdf":
            extractor = PDFExtractor(file_data)
            text = extractor.get_text()
        elif ext in ['.txt', '.csv']:
            # 파일 크기 제한 확인
            if len(file_data) > 40 * 1024 * 1024:
                logging.info(f"Skipping file {file_name} as it exceeds the size limit.")
                return text

            # 한글 포함 여부 확인
            try:
                decoded_text = read_file_with_different_encodings(file_data)
                if not contains_hangul(decoded_text):
                    logging.info(f"Skipping file {file_name} as it does not contain Hangul.")
                    return text
                else:
                    text = decoded_text
            except Exception as e:
                logging.error(f"Error decoding file {file_name}: {e}")
                return text
        elif ext == ".zip":
            try:
                with zipfile.ZipFile(BytesIO(file_data), 'r') as zipf:
                    for info in zipf.infolist():
                        if info.is_dir():
                            continue  # 디렉터리는 건너뛰기
                        
                        with zipf.open(info.filename) as file:
                            inner_ext = os.path.splitext(info.filename)[1].lower() # 파일의 확장자를 소문자로 변환하여 가져온다.
                            inner_file_data = file.read() # 파일의 데이터를 읽어온다.
                            inner_text = extract_text(inner_file_data, inner_ext) # 파일 데이터와 확장자를 사용하여 텍스트를 추출한다. (재귀적으로 호출)
                            if inner_text:   # 추출된 텍스트가 비어 있지 않다면 (내용이 있다면)
                                text += f"File: {info.filename}\n{inner_text}\n\n"
            except zipfile.BadZipFile:
                logging.error(f"Failed to process ZIP file {file_name}")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
        else:
            print(f"지원하지 않는 파일 형식: {ext}")
    except Exception as e:
        logging.error(f"Error occurred during text extraction: {e}, File Extension: {ext}")
    return text.strip()



def calculate_hash(file_data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_data)
    return sha256_hash.hexdigest()

def save_metadata_and_blob_to_db(conn, metadata, blob_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO files (file_path, hash_value, plain_text, m_time, a_time, c_time, blob_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', metadata + (blob_data,))
    conn.commit()

def process_byte_data(byte_data, file_extension, conn):
    if file_extension.lower() in whitelist_extensions:
        try:
            blob_data = sqlite3.Binary(byte_data)
            hash_value = calculate_hash(byte_data)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files (hash_value, blob_data)
                VALUES (?, ?)
            ''', (hash_value, blob_data))
            conn.commit()

        except Exception as e:
            print(f"데이터 처리 중 오류 발생: {e}")
                    
# DB 연결 및 테이블 생성 부분에서 blob_data 컬럼 추가
conn = sqlite3.connect('parsing.sqlite')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    hash_value TEXT NOT NULL,
    plain_text TEXT,
    m_time TEXT NOT NULL,
    a_time TEXT NOT NULL,
    c_time TEXT NOT NULL,
    blob_data BLOB
)
''')

# 화이트리스트 확장자
whitelist_extensions = ('.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt','.zip','.7z')

# DB 연결 종료
conn.close()