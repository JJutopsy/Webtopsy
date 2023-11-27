import os
import pytsk3
import logging
import sys
import sqlite3
from . import parsing
from datetime import datetime
import threading

def get_db_connection(db_path):
    if db_path is None:
        raise ValueError("DB path is None. Please check if the database path is correctly provided.")
    return sqlite3.connect(db_path)




# 기존 로거 가져오기
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 콘솔 핸들러 추가
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# 파일 핸들러 추가
file_handler = logging.FileHandler("log.txt", mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

db_thread_local = threading.local()

# 원하는 확장자 목록
desired_extensions = [
    '.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv','txt','zip']

# 디렉터리 처리 함수
def process_directory(directory, fs_info, relative_path, db_path=None):
    logging.info(f"db_path in process_directory: {db_path}")
    for directory_entry in directory:
        try:
            if directory_entry.info.meta is None:
                continue

            if directory_entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                sub_directory = directory_entry.as_directory()
                sub_directory_name = directory_entry.info.name.name.decode()

                if sub_directory_name not in ['.', '..']:
                    path = os.path.join(relative_path, sub_directory_name)
                    logging.info(f"Processing directory: {path}")
                    process_directory(sub_directory, fs_info, path, db_path)

            elif directory_entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
                file_name = directory_entry.info.name.name.decode()
                _, ext = os.path.splitext(file_name)
                
                logging.info(f"Checking file: {os.path.join(relative_path, file_name)} with extension {ext}")

                if ext.lower() in desired_extensions:
                    logging.info(f"Found file: {os.path.join(relative_path, file_name)}")
                    extract_file(directory_entry, fs_info, file_name, relative_path, db_path)

        except Exception as e:
            logging.error(f"Error occurred while processing directory: {e}")
            continue

# 파일 추출 함수
def extract_file(directory_entry, fs_info, file_name, relative_path, db_path):
    try:
        file_object = fs_info.open_meta(inode=directory_entry.info.meta.addr)
        file_data = file_object.read_random(0, file_object.info.meta.size)
        ext = os.path.splitext(file_name)[1].lower()

        c_time, m_time, a_time = get_file_metadata(directory_entry)
        logging.info("File Metadata - Creation Time: %s, Modification Time: %s, Access Time: %s", c_time, m_time, a_time)

        file_text = parsing.extract_text(file_data, ext)
        hash_value = parsing.calculate_hash(file_data)

        blob_data = sqlite3.Binary(file_data)

        file_info = (os.path.join(relative_path, file_name), hash_value, file_text, str(m_time), str(a_time), str(c_time))
        conn = get_db_connection(db_path)
        parsing.save_metadata_and_blob_to_db(conn, file_info, blob_data)
        conn.close()
        logging.info("Data saved to DB: %s", file_info[:6])

    except Exception as e:
        logging.error("Failed to extract or save data for file: %s, Error: %s", file_name, str(e))
        logging.exception(e)


# 파일 메타데이터 추출 함수
def get_file_metadata(directory_entry):
    c_time = datetime.fromtimestamp(directory_entry.info.meta.crtime)
    m_time = datetime.fromtimestamp(directory_entry.info.meta.mtime)
    a_time = datetime.fromtimestamp(directory_entry.info.meta.atime)
    return c_time, m_time, a_time

def process_dd(image_path, parsing_db_path):
    logging.info(f"Processing DD image. Image path: {image_path}, DB path: {parsing_db_path}")
    try:
        logging.info(f"Original image path: {image_path}")
        image_path = os.path.abspath(image_path)
        logging.info(f"Absolute image path: {image_path}")

        logging.info(f"Entered process_dd with image_path: {image_path}, parsing_db_path: {parsing_db_path}")
        conn = get_db_connection(parsing_db_path)
        logging.info("Connected to parsing database")

        # Img_Info 인스턴스 생성
        img_info = pytsk3.Img_Info(image_path)

        # 파일 시스템을 직접 오픈
        fs_info = pytsk3.FS_Info(img_info)

        # 디렉터리 순회
        directory = fs_info.open_dir(path="/")

        db_path = parsing_db_path  # db_path 정의
        process_directory(directory, fs_info, "", db_path=db_path)  # db_path 전달

        conn.close()
        logging.info("All files processed.")
        return True, "Processing successful"
    except Exception as e:
        logging.error(f"An error occurred while processing DD file: {e}")
        return False, str(e)
