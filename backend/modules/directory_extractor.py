import hashlib
import sqlite3
import time
import zipfile
import logging
import os
from pathlib import Path
from io import BytesIO
from .ole_extractor import OLEExtractor
from .hwp_extractor import HWPExtractor
from .docx_extractor import DOCXExtractor
from .pptx_extractor import PPTXExtractor
from .xlsx_extractor import XLSXExtractor
from .pdf_extractor import PDFExtractor
import threading
from . import parsing
from .eml_extractor import EmlParser
from .directory_pst_extractor import PSTParser

db_thread_local = threading.local()

def get_db_connection(db_path):
    return sqlite3.connect(db_path)

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
        elif ext == ".eml":
            return file_data
        elif ext == ".pst":
            return file_data
        elif ext in [".txt", ".csv"]:
            text = read_file_with_different_encodings(file_data)
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

def process_files_in_directory(directory, conn, parsingDBpath):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            
            if file_extension in whitelist_extensions:
                with open(file_path, 'rb') as f:
                        file_data = f.read()
                        try:
                            if file_extension == '.eml':
                                emlfile = extract_text(file_data, '.eml') #eml일 경우 그냥 바이트 스트림 형식으로 된 eml 파일을 반환함
                                # EML 데이터를 사용하여 EmlParser 인스턴스를 생성
                                parser = EmlParser(emlfile)
                                # EML 파일 정보 추출
                                (subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body) = parser.process_eml()
                                (attachments) = parser.extract_attachments()
                                save_location = file_path
                                emlfile_info = (save_location, subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body)
                                logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                                save_metadata_and_blob_to_db_emlVersion(conn, emlfile_info)
                                logging.info("Data saved to DB: %s", emlfile_info)  # DB에 데이터 저장 후 로깅
                                if attachments:
                                    for filename, content_type, body, plain_text in attachments:
                                        Fn = filename
                                        Ct = content_type
                                        Body = body
                                        pt = plain_text
                                        md5_hash = calculate_hash(Body)
                                        emlBlobData = sqlite3.Binary(Body)
                                        emlAttachments_info = (save_location, Fn, md5_hash, emlBlobData, pt)
                                        logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                                        save_metadata_and_blob_to_db_emlAttachmentsVersion(conn, emlAttachments_info)
                                        logging.info("Data saved to DB: %s", emlfile_info)  # DB에 데이터 저장 후 로깅
                            if file_extension == '.pst':
                                pstfile = extract_text(file_data, '.pst')
                                parser = PSTParser(pstfile,directory)
                                parser.extract_emails_from_pst(conn)
                                conn = sqlite3.connect(parsingDBpath)
                                
                            if file_extension != '.eml' and file_extension != '.pst':
                                    with open(file_path, 'rb') as f:
                                        file_data = f.read()
                                        blob_data = sqlite3.Binary(file_data)
                                        hash_value = calculate_hash(file_data)
                                        plain_text = extract_text(file_data, file_extension)
                                        stat = os.stat(file_path)
                                        m_time = time.ctime(stat.st_mtime)
                                        a_time = time.ctime(stat.st_atime)
                                        c_time = time.ctime(stat.st_ctime)
                                                
                                        metadata = (file_path, hash_value, plain_text, m_time, a_time, c_time)
                                        save_metadata_and_blob_to_db(conn, metadata, blob_data)
                        except Exception as e:
                            logging.error(f"Error processing file {file_path}: {e}")

def save_metadata_and_blob_to_db_emlAttachmentsVersion(conn, fileinfo):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emlAttachments (save_location, filename, hash, data, plain_text)
        VALUES (?, ?, ?, ?, ?)
    ''',fileinfo)
    conn.commit()

def save_metadata_and_blob_to_db_emlVersion(conn,fileinfo):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emlEmails (save_location, subject, date, sender, receiver, ctime, mtime, atime, hash, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',fileinfo)
    conn.commit()

def save_metadata_and_blob_to_db_pstVersion(conn, fileinfo):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pstEmails (save_location, subject, date, sender, receiver, hash, body)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''',fileinfo)
    conn.commit()
    
def save_metadata_and_blob_to_db_pstAttachmentsVersion(conn, fileinfo):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pstAttachments (save_location, subject, filename, hash, data)
        VALUES (?, ?, ?, ?, ?)
    ''',fileinfo)
    conn.commit()

def process_directories(directories, parsingDBpath):
    try:
        # 데이터베이스에 직접 연결
        conn = sqlite3.connect(parsingDBpath)
        
        for directory in directories:
            process_files_in_directory(directory, conn, parsingDBpath)
        
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return 500, "Internal Server Error"
    except Exception as e:
        logging.error(f"Exception in _query: {e}")
        return 500, "Internal Server Error"
    finally:
        if conn:
            conn.close()

    return 200, "Success"
    
# DB 연결 및 테이블 생성 부분에서 blob_data 컬럼 추가

# 화이트리스트 확장자
whitelist_extensions = ('.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt','.zip','.7z')


# get_parsing_db_path 함수 정의 (casedb에서 parsingDBpath 값을 조회)
def get_parsing_db_path(case_id):
    try:
        casedb_conn = sqlite3.connect('casedb.sqlite')
        cursor = casedb_conn.cursor()
        cursor.execute("SELECT parsingDBpath FROM cases WHERE id = ?", (case_id,))
        result = cursor.fetchone()
        casedb_conn.close()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        return None