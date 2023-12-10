import os
import pytsk3
import pyewf
import logging
import sys
import sqlite3
from . import parsing
from datetime import datetime
import threading
from .eml_extractor import EmlParser
from .pst_eml_extractor import PSTParser

db_thread_local = threading.local()

def get_db_connection(db_path):
    return sqlite3.connect(db_path)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 원하는 확장자 목록
desired_extensions = [
    '.doc', '.docx', '.pptx', '.xlsx', '.pdf', '.hwp', '.eml',
    '.pst', '.ost', '.ppt', '.xls', '.csv', '.txt','.zip'
]

# DB 연결
conn = sqlite3.connect('parsing.sqlite')

# E01 파일을 처리하는 클래스
class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()

# 디렉터리 처리 함수
def process_directory(directory, fs_info, relative_path, db_path,image_path):
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
                    extract_file(directory_entry, fs_info, file_name, relative_path, db_path,image_path)

        except Exception as e:
            logging.error(f"Error occurred while processing directory: {e}")
            continue

# 파일 추출 함수
def extract_file(directory_entry, fs_info, file_name, relative_path, db_path,image_path):
    try:
        file_object = fs_info.open_meta(inode=directory_entry.info.meta.addr)
        file_data = file_object.read_random(0, file_object.info.meta.size)
        logging.info("File data length: %d", len(file_data))  # 파일 데이터 길이 로깅
        ext = os.path.splitext(file_name)[1].lower()  # 파일 확장자 추출
        conn = get_db_connection(db_path)

        if ext == '.eml':
            emlfile = parsing.extract_text(file_data, ext) #eml일 경우 그냥 바이트 스트림 형식으로 된 eml 파일을 반환함
            # EML 데이터를 사용하여 EmlParser 인스턴스를 생성
            parser = EmlParser(emlfile)

            # EML 파일 정보 추출
            (subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body) = parser.process_eml()
            (attachments) = parser.extract_attachments()
            
            save_location = os.path.join(relative_path, file_name)
               
            emlfile_info = (save_location, subject, date, from_, to, ctime, mtime, atime, md5_hash, mail_body)
            
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
                    emlAttachments_info = (save_location, Fn, md5_hash, emlBlobData, pt)
                    logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
                    parsing.save_metadata_and_blob_to_db_emlAttachmentsVersion(conn, emlAttachments_info)
                    logging.info("Data saved to DB: %s", emlAttachments_info)  # DB에 데이터 저장 후 로깅
           
        if ext == ".pst":
            pstfile = parsing.extract_text(file_data, ext)
            parser = PSTParser(pstfile)
            psteml = parser.extract_emails_from_pst()
            save_location = os.path.join(relative_path, file_name)
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
            c_time, m_time, a_time = get_file_metadata(directory_entry)
            logging.info("File Metadata - Creation Time: %s, Modification Time: %s, Access Time: %s", c_time, m_time, a_time)

            file_text = parsing.extract_text(file_data, ext)  # 파일 확장자 전달
            
            hash_value = parsing.calculate_hash(file_data)  
            logging.info("Calculated hash: %s", hash_value)  # 계산된 해시 값 로깅

            blob_data = sqlite3.Binary(file_data)

            file_info_log = (os.path.join(relative_path, file_name), hash_value, m_time.strftime("%Y-%m-%d %H:%M:%S"), a_time.strftime("%Y-%m-%d %H:%M:%S"), c_time.strftime("%Y-%m-%d %H:%M:%S"))
            file_info = (image_path+"\\"+os.path.join(relative_path, file_name), hash_value, file_text, m_time.strftime("%Y-%m-%d %H:%M:%S"), a_time.strftime("%Y-%m-%d %H:%M:%S"), c_time.strftime("%Y-%m-%d %H:%M:%S"))
            logging.info("File info before saving to DB: %s", str(file_info_log))  # file_info 변수의 일부 값을 로깅으로 확인

            logging.info("Saving data to DB...")  # DB에 데이터 저장 전 로깅
            parsing.save_metadata_and_blob_to_db(conn, file_info, blob_data)
            logging.info("Data saved to DB: %s", file_info_log)  # DB에 데이터 저장 후 로깅

    except Exception as e:
        logging.exception("Exception occurred while processing the file: %s", file_name)

        
# 파일 메타데이터 추출 함수
def get_file_metadata(directory_entry):
    c_time = datetime.fromtimestamp(directory_entry.info.meta.crtime)
    m_time = datetime.fromtimestamp(directory_entry.info.meta.mtime)
    a_time = datetime.fromtimestamp(directory_entry.info.meta.atime)
    return c_time, m_time, a_time

def process_e01(image_path, parsing_db_path):
    try:
        logging.info(f"Original image path: {image_path}")
        image_path = os.path.abspath(image_path)
        logging.info(f"Absolute image path: {image_path}")

        logging.info(f"Entered process_e01 with image_path: {image_path}, parsing_db_path: {parsing_db_path}")
        conn = get_db_connection(parsing_db_path)
        logging.info("Connected to parsing database")
        
        ab_path = parsing_db_path
        
        # EWF 파일 핸들을 얻음
        filenames = pyewf.glob(image_path)
        ewf_handle = pyewf.handle()
        ewf_handle.open(filenames)
        
        # EWFImgInfo 인스턴스 생성
        ewf_img_info = EWFImgInfo(ewf_handle)
        
        # 파일 시스템을 직접 오픈
        fs_info = pytsk3.FS_Info(ewf_img_info)
        
        # 디렉터리 순회
        directory = fs_info.open_dir(path="/")
        
        db_path = parsing_db_path  # db_path 정의
        process_directory(directory, fs_info, "", db_path,image_path) # db_path 전달
        
        # 리소스 정리
        ewf_img_info.close()
        logging.info("All files processed.")
        return True, "Processing successful"
    except Exception as e:
        logging.error(f"An error occurred while processing E01 file: {e}")
        return False, str(e)

# if __name__ == "__main__":
#   result = process_e01("D:/test.E01", "cases/성심당 사건8/parsing.sqlite")
#    if result:
#        print("E01 File Processing Completed Successfully")
#    else:
#        print("E01 File Processing Failed")