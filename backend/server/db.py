import os
import sqlite3

# 현재 스크립트 파일의 절대 경로를 구합니다.
current_file_path = os.path.abspath(__file__)

# 현재 스크립트 파일이 있는 디렉토리의 경로를 구합니다.
current_dir_path = os.path.dirname(current_file_path)

# 데이터베이스 파일의 경로를 현재 디렉토리 기준으로 설정합니다.
DATABASE_FILE = os.path.join(current_dir_path, 'users.sqlite')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    return conn, cursor

def initialize_database():
    conn, cursor = get_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL,
        nickname TEXT,
        session_key TEXT
    )
    ''')
    conn.commit()
    conn.close()

def init_casedb():
    conn = sqlite3.connect('casedb.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY,
        casename TEXT NOT NULL,
        caseinfo TEXT,
        username TEXT,
        parsingDBpath TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    
def init_tables_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # files 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        hash_value TEXT NOT NULL,
        plain_text TEXT,
        m_time TEXT NOT NULL,
        a_time TEXT NOT NULL,
        c_time TEXT NOT NULL,
        blob_data BLOB,
        tag TEXT,
        nnp TEXT
    )
    ''')
    
    # artifacts 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artifacts (
        name TEXT,
        text TEXT,
        m_time TEXT,
        a_time TEXT,
        c_time TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlEmails (
        save_location TEXT,
        md5_hash TEXT,
        subject TEXT,
        date TEXT,
        sender TEXT,
        receiver TEXT,
        ctime TEXT,
        mtime TEXT,
        atime TEXT,
        mail_body TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlAttachments (
        email_save_location TEXT,
        filename TEXT,
        hash TEXT,
        data BLOB
    )
    ''')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT NOT NULL,
        context TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        type TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()