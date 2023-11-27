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
    
    cursor.execute('''
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

    cursor.execute('''
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
    
    cursor.execute('''
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emlPerson (
        emlPerson TEXT,
        relatedPerson TEXT
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
    # DocumentMetadata 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DocumentMetadata (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FilePath TEXT NOT NULL,      -- 문서의 파일 경로
    FileName TEXT NOT NULL,      -- 문서의 파일 이름
    FileSize INTEGER,            -- 파일 크기
    SHA256Hash TEXT,             -- 파일 내용의 해시 값

    -- core.xml 메타데이터
    Title TEXT,                  -- 문서 제목
    Author TEXT,                 -- 문서 작성자
    Subject TEXT,                -- 문서 주제
    Keywords TEXT,               -- 문서 키워드
    Description TEXT,            -- 문서 설명
    LastModifiedBy TEXT,         -- 마지막으로 수정한 사용자
    ModificationDate TEXT,       -- 수정 날짜
    CreationDate TEXT,           -- 생성 날짜
    LastPrintedDate TEXT,        -- 마지막으로 인쇄된 날짜

    -- App.xml 메타데이터
    Template TEXT,               -- 사용된 템플릿
    TotalPageCount INTEGER,      -- 총 페이지 수
    WordCount INTEGER,           -- 단어 수
    CharacterCount INTEGER,      -- 문자 수
    ParagraphCount INTEGER,      -- 문단 수
    SlideCount INTEGER,          -- 슬라이드 수 (PPTX)
    NoteCount INTEGER,           -- 노트 수 (PPTX)
    HiddenSlideCount INTEGER,    -- 숨겨진 슬라이드 수 (PPTX)
    MultimediaClipCount INTEGER, -- 멀티미디어 클립 수 (PPTX)

    -- style.xml (스타일 및 포맷팅 정보는 복잡할 수 있으므로 JSON이나 XML 형태로 저장 함)
    StylesJSON TEXT,             -- JSON 형식의 스타일 정보
    FormattingXML TEXT,          -- XML 형식의 포맷팅 정보

    -- ms office 버전
    ApplicationVersion TEXT      -- 문서를 생성한 애플리케이션 버전
    )
    """)

    # 데이터베이스에 미디어 파일 정보를 저장하기 위한 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MediaFiles (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    DocumentID INTEGER,          -- 관련 문서 ID
    OriginalFileName TEXT,       -- 미디어 파일의 원본 이름
    SHA256Hash TEXT,             -- 파일 내용의 해시 값
    FileSize INTEGER,            -- 파일 크기
    FileData BLOB,               -- 미디어 파일 데이터
    FOREIGN KEY(DocumentID) REFERENCES DocumentMetadata(ID)
    )
    """)
    conn.commit()
    conn.close()
