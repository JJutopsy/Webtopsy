from flask import Blueprint, request, jsonify
import os
import sqlite3
import logging
import threading
import time
from .db import init_casedb, init_tables_db
from modules import e01_extractor, dd_extractor, zip_extractor, directory_extractor, xml_extractor
from modules.tag_extractor import KeywordExtractor
from modules.ner_extractor import NERExtractor
from modules.nnp_extractor import NNPExtractor
from modules.emlperson_extractor import EmlPersonUpdater

newcase_bp = Blueprint('newcase', __name__)

logging.basicConfig(level=logging.INFO)
_db_thread_local = threading.local()

def get_db():
    init_casedb()
    if not hasattr(_db_thread_local, "conn"):
        _db_thread_local.conn = sqlite3.connect('casedb.sqlite')
    return _db_thread_local.conn, _db_thread_local.conn.cursor()

@newcase_bp.route('/newcase', methods=['POST'])
def new_case():
    data = request.json
    casename = data['casename']
    caseinfo = data.get('caseinfo', '')  
    filesWithOwners = data['filesWithOwners']
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

    # 데이터베이스에서 같은 이름을 가진 케이스 검색
    cursor.execute('SELECT casename FROM cases WHERE casename LIKE ?', (casename + '%',))
    existing_cases = cursor.fetchall()
    logging.info("Existing cases: %s", existing_cases)

    # 같은 이름을 가진 케이스가 존재한다면, 새로운 이름 생성
    if existing_cases:
        existing_numbers = [int(name[0].replace(casename, "")) for name in existing_cases if name[0].replace(casename, "").isdigit()]
        new_number = max(existing_numbers) + 1 if existing_numbers else 1
        new_casename = casename + str(new_number)
    else:
        new_casename = casename

    results['casename'] = new_casename  # 결과에 새로운 케이스 이름 업데이트
    logging.info("New casename: %s", new_casename)

    # 케이스 폴더 생성
    case_folder_path = os.path.join('cases', new_casename).replace('\\', '/')
    if os.path.exists(case_folder_path):
        conn.close()  # 데이터베이스 연결 닫기
        return jsonify({"error": "Case folder already exists unexpectedly. Please try again."}), 500
    os.makedirs(case_folder_path)

    # 파싱 데이터베이스 경로 설정
    parsingDBpath = os.path.join(case_folder_path, 'parsing.sqlite').replace('\\', '/')
    logging.info("parsingDBpath: %s", parsingDBpath)

    # 데이터베이스 연결 및 커서 생성
    parsing_conn = sqlite3.connect(parsingDBpath)
    init_tables_db(parsingDBpath)

    # 커밋 및 연결 닫기
    parsing_conn.commit()
    parsing_conn.close()

    # 데이터베이스에 케이스 정보 및 파싱 데이터베이스 경로 저장
    cursor.execute('INSERT INTO cases (casename, caseinfo, parsingDBpath) VALUES (?, ?, ?)',
                   (new_casename, caseinfo, parsingDBpath))
    conn.commit()
    case_id = cursor.lastrowid
    logging.info("Case ID: %s", case_id)

    for fileInfo in filesWithOwners:
        filePath = fileInfo['current']
        owner = fileInfo['owner']
        detail, item = process_item(filePath, parsingDBpath)
        if owner and item:
            update_owner(parsingDBpath, item, owner)

        xml_extractor.process_files(parsingDBpath)
        results['details'].append(detail)

    # files 테이블에 대한 NNP와 태그 데이터 업데이트
    if nnp or tag:
        update_tags_based_on_text(parsingDBpath, nnp, tag)

    # NNP 처리
    if nnp:
        try:
            nnp_extractor = NNPExtractor(parsingDBpath)
            nnp_extractor.process_texts_eml()
            nnp_extractor.process_texts_emlAttachments()
            nnp_extractor.process_texts_pstAttachments()
        except Exception as e:
            logging.error(f"Error processing NNP for emlEmails: {e}")

    # 태그 처리
    if tag:
        try:
            tag_extractor = KeywordExtractor(parsingDBpath)
            tag_extractor.extract_keywords_eml()
            tag_extractor.extract_keywords_emlAttachments()
            tag_extractor.extract_keywords_pstAttachments()
        except Exception as e:
            logging.error(f"Error processing TAG for emlEmails: {e}")

    # EmlPerson 업데이트
    try:
        eml_person_updater = EmlPersonUpdater(parsingDBpath)
        eml_person_updater.update_eml_person_table()
    except Exception as e:
        logging.error(f"Error updating EmlPerson table: {e}")

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
        logging.error(f"An error occurred while calling process_e01: {str(e)}")
        detail['status'], detail['message']= 500, str(e)
    return detail, item


def update_owner(db_path, file_path, owner):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.info(f"Updating owner for file_path: {file_path} with owner: {owner}")
        owner = file_path+","+owner
        cursor.execute("UPDATE files SET owner = ? WHERE file_path LIKE ?;", (owner, file_path + '%'))
        conn.commit()
    except Exception as e:
        logging.error(f"Error in update_owner: {e}")
    finally:
        conn.close()

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