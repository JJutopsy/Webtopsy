from flask import Blueprint, request, jsonify
import os
import sqlite3
import logging
import threading
import time
from .db import init_casedb
from modules import e01_extractor, dd_extractor, zip_extractor, directory_extractor

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
    casedata = data['casedata']
    total = data['total']

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
    parsing_cursor = parsing_conn.cursor()

    # 파싱 데이터베이스에 files 테이블 생성
    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        hash_value TEXT NOT NULL,
        plain_text TEXT,
        m_time TEXT NOT NULL,
        a_time TEXT NOT NULL,
        c_time TEXT NOT NULL,
        tag TEXT,
        NNP TEXT,
        blob_data BLOB
    )
    ''')
    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT NOT NULL,
        context TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        type TEXT NOT NULL
    )
    ''')
    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlEmails (
        save_location TEXT,
        subject TEXT,
        date TEXT,     
        sender TEXT,
        receiver TEXT,
        ctime TEXT,
        mtime TEXT,
        atime TEXT,
        hash TEXT,
        body TEXT,
        tag TEXT,
        NNP TEXT
    )
    ''')

    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlAttachments (
        save_location TEXT,
        filename TEXT,
        hash TEXT,
        data BLOB,
        plain_text TEXT,
        tag TEXT,
        NNP TEXT
    )
    ''')
    
    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS pstAttachments (
        save_location TEXT,
        subject TEXT,
        filename TEXT,
        hash TEXT,
        data BLOB,
        plain_text TEXT,
        tag TEXT,
        NNP TEXT
    )
    ''')
    
    parsing_cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlPerson (
        emlPerson TEXT,
        relatedPerson TEXT
    )
    ''')
    # 커밋 및 연결 닫기
    parsing_conn.commit()
    parsing_conn.close()

    # 데이터베이스에 케이스 정보 및 파싱 데이터베이스 경로 저장
    cursor.execute('INSERT INTO cases (casename, caseinfo, parsingDBpath) VALUES (?, ?, ?)',
                   (new_casename, caseinfo, parsingDBpath))
    conn.commit()
    case_id = cursor.lastrowid
    logging.info("Case ID: %s", case_id)

    for item in casedata:
        detail = process_item(item, parsingDBpath)
        results['details'].append(detail)

    conn.close()  # 데이터베이스 연결 닫기
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
    return detail