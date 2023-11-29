import sqlite3
import os
from io import BytesIO
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET
from hashlib import sha256
import zipfile
import io



# OOXML 파일이 맞는지 확인하는 함수
def is_ooxml(filename):
    ooxml_extensions = ['.docx', '.xlsx', '.pptx']
    _, extension = os.path.splitext(filename)
    return extension in ooxml_extensions

# OOXML 파일에서 메타데이터를 추출하는 함수
def parse_metadata(blob_data, xml_file):
    try:
        with ZipFile(BytesIO(blob_data), 'r') as zip:
            with zip.open(xml_file) as xml:
                tree = ET.parse(xml)
                root = tree.getroot()
                metadata = {child.tag.split('}')[-1]: child.text for child in root}
                return metadata
    except (BadZipFile, KeyError):
        print("Unable to parse metadata")
        return {}

# 데이터베이스에 메타데이터를 저장하는 함수
def save_metadata(conn, filename, metadata):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS documentmetadata (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT);")
    conn.commit()

    cursor.execute("PRAGMA table_info(documentmetadata);")
    existing_columns = {info[1] for info in cursor.fetchall()}

    for key in metadata.keys():
        if key not in existing_columns:
            cursor.execute(f'ALTER TABLE documentmetadata ADD COLUMN "{key}" TEXT;')
            conn.commit()

    cursor.execute("SELECT * FROM documentmetadata WHERE filename = ?", (filename,))
    row = cursor.fetchone()

    if row is None:
        columns = '", "'.join(metadata.keys())
        placeholders = ', '.join('?' * len(metadata))
        sql = f'INSERT INTO documentmetadata ("filename", "{columns}") VALUES (?, {placeholders})'
        values = [filename] + list(metadata.values())
        cursor.execute(sql, values)
        conn.commit()
    else:
        for key, value in metadata.items():
            if row[key] is None:
                sql = f'UPDATE documentmetadata SET "{key}" = ? WHERE filename = ?'
                cursor.execute(sql, (value, filename))
                conn.commit()

# 미디어 파일 정보를 MediaFiles 테이블에 삽입하는 함수
def insert_media_file(document_id, original_file_name, file_data, source_file_name, cursor):
    file_size = len(file_data)
    sha256_hash = sha256(file_data).hexdigest()
    cursor.execute("""
        INSERT INTO MediaFiles (DocumentID, OriginalFileName, SourceFileName, SHA256Hash, FileSize, FileData)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (document_id, original_file_name, source_file_name, sha256_hash, file_size, file_data))

# OOXML 파일에서 미디어 파일을 추출하고 MediaFiles 테이블에 저장하는 함수
def extract_media_from_blob(document_id, blob_data, source_file_name, cursor, skipped_files):
    try:
        with zipfile.ZipFile(io.BytesIO(blob_data), 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.startswith(('word/media/', 'ppt/media/', 'xl/media/')):
                    try:
                        file_data = zip_ref.read(file_info.filename)
                        insert_media_file(document_id, file_info.filename, file_data, source_file_name, cursor)
                    except Exception as e:
                        print(f"Error reading file {file_info.filename} in document {document_id}: {e}")
                        skipped_files.append(f"{source_file_name}/{file_info.filename}")
    except BadZipFile:
        print(f"Document ID {document_id} is not a valid OOXML format.")

# 파일 데이터를 처리하는 함수

def process_files(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        skipped_files = []

        cursor.execute("SELECT id, file_path, blob_data FROM files")
        rows = cursor.fetchall()
        for row in rows:
            file_path, blob_data = row['file_path'], row['blob_data']
            document_id = row['id']
            source_file_name = os.path.basename(file_path)

            if is_ooxml(file_path):
                for xml_file in ['docProps/app.xml', 'docProps/core.xml']:
                    metadata = parse_metadata(blob_data, xml_file)
                    save_metadata(conn, file_path, metadata)
                extract_media_from_blob(document_id, blob_data, source_file_name, cursor, skipped_files)

    return skipped_files
