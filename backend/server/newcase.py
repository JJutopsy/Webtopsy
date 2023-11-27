from flask import Blueprint, request, jsonify
import os
import sqlite3
import logging
import time
import zipfile
import io
import threading
from .db import init_casedb, init_tables_db
from modules import e01_extractor, dd_extractor, zip_extractor, directory_extractor
from modules.tag_extractor import KeywordExtractor
from modules.ner_extractor import NERExtractor
from lxml import etree


newcase_bp = Blueprint('newcase', __name__)

logging.basicConfig(level=logging.INFO)
_db_thread_local = threading.local()

def get_db():
    init_casedb()
    if not hasattr(_db_thread_local, "conn"):
        _db_thread_local.conn = sqlite3.connect('casedb.sqlite')
    return _db_thread_local.conn, _db_thread_local.conn.cursor()

def summarize_extensions(parsingDBpath):
    conn = sqlite3.connect(parsingDBpath)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM files")  # 'files' 테이블의 'file_path' 컬럼에서 파일 경로를 조회합니다.
    files = cursor.fetchall()
    extension_count = {}
    for file in files:
        extension = os.path.splitext(file[0])[1].lower()
        if extension in extension_count:
            extension_count[extension] += 1
        else:
            extension_count[extension] = 1
    conn.close()
    return extension_count
    
@newcase_bp.route('/newcase', methods=['POST'])
def new_case():
    data = request.json
    casename = data['casename']
    caseinfo = data.get('caseinfo', '')  
    casedata = data['casedata']
    total = data['total']
    nnp = data.get('nnp', False)
    tag = data.get('tag', False)
    results = {
        "casename": casename,
        "caseinfo": caseinfo,
        "total": total,
        "details": []
    }

    conn, cursor = get_db()

    # 기존 케이스 이름 검색
    cursor.execute('SELECT casename FROM cases WHERE casename LIKE ?', (casename + '%',))
    existing_cases = [row[0] for row in cursor.fetchall()]

    new_casename = casename
    suffix = 1
    while True:
        if new_casename in existing_cases:
            new_casename = f"{casename}{suffix}"
            suffix += 1
        else:
            case_folder_path = os.path.join('cases', new_casename).replace('\\', '/')
            if not os.path.exists(case_folder_path):
                os.makedirs(case_folder_path)
                logging.info(f"Created case folder: {case_folder_path}")
                break
            else:
                existing_cases.append(new_casename)
                new_casename = f"{casename}{suffix}"
                suffix += 1

    results['casename'] = new_casename
    logging.info("New casename: %s", new_casename)

    # 파싱 데이터베이스 경로 설정
    parsingDBpath = os.path.join(case_folder_path, 'parsing.sqlite').replace('\\', '/')
    logging.info("parsingDBpath: %s", parsingDBpath)
    # 파싱 데이터베이스에 TABLE 생성
    init_tables_db(parsingDBpath)
    
    parsing_conn = sqlite3.connect(parsingDBpath)
    parsing_cursor = parsing_conn.cursor()

    parsing_conn.commit()
    parsing_conn.close()
    
    cursor.execute('INSERT INTO cases (casename, caseinfo, parsingDBpath) VALUES (?, ?, ?)', (new_casename, caseinfo, parsingDBpath))
    conn.commit()
    case_id = cursor.lastrowid
    logging.info("Case ID: %s", case_id)

    for item in casedata:
        detail = process_item(item, parsingDBpath)
        results['details'].append(detail)
    # 메타데이터 추출 로직 호출
    # extract_and_save_ooxml_metadata(parsingDBpath)
    if nnp or tag:
        update_tags_based_on_text(parsingDBpath, tag, nnp)
    conn.close()
    return jsonify(results)


def process_item(item, parsingDBpath):
    logging.info(f"Processing item: {item}")
    detail = {
        "filepath": item,
        "status": None,
        "message": None
    }
    try:
        if os.path.isdir(item):
            # 디렉터리 처리
            logging.info(f"Calling Directory with item: {item}, parsingDBpath: {parsingDBpath}")
            result = directory_extractor.process_directories([item], parsingDBpath)
            logging.info(f"Result from Directories: {result}, Type: {type(result)}")
            if result is None:
                detail['status'], detail['message'] = 500, "Directory processing failed"
            else:
                detail['status'], detail['message'] = result

        elif os.path.isfile(item):
            extension = os.path.splitext(item)[1].lower()
            if extension == '.e01':
                logging.info(f"Calling process_e01 with item: {item}, parsingDBpath: {parsingDBpath}")
                result = e01_extractor.process_e01(item, parsingDBpath)
                logging.info(f"Result from process_e01: {result}, Type: {type(result)}")
                detail['status'], detail['message'] = result
            elif extension in ('.001', '.dd'):
                logging.info(f"Calling process_dd with item: {item}, parsingDBpath: {parsingDBpath}")
                detail['status'], detail['message'] = dd_extractor.process_dd(item, parsingDBpath)
            elif extension == '.zip':
                logging.info(f"Calling process_zip with item: {item}, parsingDBpath: {parsingDBpath}")
                result = zip_extractor.process_zip(item, parsingDBpath)
                logging.info(f"Result from process_zip: {result}, Type: {type(result)}")
                detail['status'], detail['message'] = result
            else:
                # 지원하지 않는 파일 형식
                detail['status'], detail['message'] = 400, "Unsupported file type"
        else:
            # 존재하지 않는 경로
            detail['status'], detail['message'] = 404, "Path does not exist"
    except Exception as e:
        logging.error(f"An error occurred while calling process_item: {str(e)}")
        detail['status'], detail['message']= 500, str(e)
    return detail

def update_tags_based_on_text(parsingDBpath, nnp, tag):
    # 데이터베이스 연결을 한 번만 엽니다.
    conn = sqlite3.connect(parsingDBpath)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    conn.commit()

    # 인스턴스를 생성합니다.
    keyword_extractor = KeywordExtractor(parsingDBpath)
    ner_extractor = NERExtractor(parsingDBpath)

    # 모든 파일에 대한 plain text 컬럼을 조회합니다.
    cursor.execute("SELECT id, plain_text FROM files")
    files = cursor.fetchall()

    # 데이터베이스에 각각의 파일에 대해 업데이트를 수행합니다.
    for file_id, plain_text in files:
        try:
            # NER 및 키워드 추출을 수행합니다.
            extracted_nnp = ner_extractor.get_nnp(plain_text) if nnp else None  # process_texts 대신 get_nnp를 사용합니다.
            extracted_tag = keyword_extractor.get_top_words(plain_text)

            # 추출된 nnp와 tag 값을 데이터베이스에 업데이트합니다.
            if extracted_nnp is not None or extracted_tag is not None:
                cursor.execute(
                    "UPDATE files SET nnp=?, tag=? WHERE id=?",
                    (extracted_nnp, extracted_tag, file_id)
                )
        except sqlite3.OperationalError as e:
            if str(e) == "database is locked":
                # 예외가 발생한 경우 로그를 남기고, 필요에 따라 백오프를 적용할 수 있습니다.
                print(f"Database is locked, retrying... (file_id={file_id})")
                time.sleep(5)  # 5초간 대기 후 재시도
                continue

    # 변경 사항을 커밋하고 연결을 닫습니다.
    conn.commit()
    conn.close()
    
# def extract_and_save_ooxml_metadata(parsingDBpath):
#     # 파일 데이터베이스 연결
#     conn = sqlite3.connect(parsingDBpath)
#     cursor = conn.cursor()
    
#     # OOXML 파일을 조회
#     cursor.execute("SELECT id, blob_data FROM files WHERE file_path LIKE '%.docx' OR file_path LIKE '%.xlsx' OR file_path LIKE '%.pptx'")
#     ooxml_files = cursor.fetchall()
    
#     for file_id, blob_data in ooxml_files:
#         # 시그니처 확인 로직 (예: '[Content_Types].xml' 존재 여부 확인)
#         try:
#             with zipfile.ZipFile(io.BytesIO(blob_data), 'r') as zipped_file:
#                 if '[Content_Types].xml' in zipped_file.namelist():
#                     # 메타데이터 추출 로직
#                     core_xml_content = zipped_file.read('docProps/core.xml')
#                     app_xml_content = zipped_file.read('docProps/app.xml')
#                     # XML 파싱
#                     core_xml_root = etree.fromstring(core_xml_content)
#                     app_xml_root = etree.fromstring(app_xml_content)
#                     # 메타데이터 추출
#                     core_metadata = extract_core_metadata(core_xml_root)
#                     app_metadata = extract_app_metadata(app_xml_root)
#                     # 추출한 메타데이터를 데이터베이스에 저장
#                     save_metadata_to_db(parsingDBpath, core_metadata, app_metadata, os.path.splitext(file_path)[1].lower())
#         except zipfile.BadZipFile:
#             logging.error(f"File ID {file_id} is not a valid OOXML file.")

#     conn.close()