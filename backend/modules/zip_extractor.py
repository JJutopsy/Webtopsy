import io
import zipfile
import logging
import sqlite3
import os
from . import parsing
from datetime import datetime
from .eml_extractor import EmlParser
from .pst_eml_extractor import PSTParser

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
                    if ext == '.eml':
                        emlfile = parsing.extract_text(file_data, ext) #eml일 경우 그냥 바이트 스트림 형식으로 된 eml 파일을 반환함
                        # EML 데이터를 사용하여 EmlParser 인스턴스를 생성
                        parser = EmlParser(emlfile)

                        # EML 파일 정보 추출
                        (subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body) = parser.process_eml()
                        (attachments) = parser.extract_attachments()
                        
                        save_location = corrected_file_name
                        emltoblob = sqlite3.Binary(emlfile)
                        emlfile_info = (save_location, subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body, emltoblob)
                        
                        logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                        parsing.save_metadata_and_blob_to_db_emlVersion(conn, emlfile_info)
                        logging.info("Data saved to DB: %s", emlfile_info)  # DB에 데이터 저장 후 로깅
                        
                        if attachments:
                            for filename, content_type, body, plain_text in attachments:
                                Fn = filename
                                Ct = content_type
                                Body = body
                                pt = plain_text
                                md5_hash = parsing.calculate_hash(Body)
                                emlBlobData = sqlite3.Binary(Body)
                                emlAttachments_info = (save_location, Fn, md5_hash, emlBlobData,pt)
                                logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                                parsing.save_metadata_and_blob_to_db_emlAttachmentsVersion(conn, emlAttachments_info)
                                logging.info("Data saved to DB: %s", emlAttachments_info)  # DB에 데이터 저장 후 로깅
                    
                    if ext == '.pst':
                        pstfile = parsing.extract_text(file_data, ext)
                        parser = PSTParser(pstfile)
                        psteml = parser.extract_emails_from_pst()
                        save_location = corrected_file_name
                        if psteml:
                            for pstdata in psteml:
                                subject = pstdata['subject']
                                sender = pstdata['sender']
                                receiver = pstdata['receiver']
                                body = pstdata['body']
                                date = pstdata['date']
                                ctime = pstdata['ctime']
                                mtime = pstdata['mtime']
                                atime = pstdata['atime']
                                
                                hash = parser.calculate_hash(body)
                                pst_info = (save_location, subject, date, sender, receiver, ctime, mtime, atime, hash, body)
                                logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                                parsing.save_metadata_and_blob_to_db_emlVersion(conn, pst_info)
                                logging.info("Data saved to DB: %s", pst_info)  # DB에 데이터 저장 후 로깅
                                
                    if ext != '.eml' and ext != '.pst':
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