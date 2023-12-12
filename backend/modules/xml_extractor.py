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

def save_metadata(conn, file_id, filename, metadata):
    cursor = conn.cursor()

    # 필터링된 메타데이터 생성 (테이블에 존재하는 컬럼만 포함)
    valid_columns = [
        "Template", "TotalTime", "Pages", "Words", "Characters", 
        "Application", "DocSecurity", "Lines", "Paragraphs", "ScaleCrop", 
        "HeadingPairs", "TitlesOfParts", "Company", "LinksUpToDate", 
        "CharactersWithSpaces", "SharedDoc", "HyperlinksChanged", "AppVersion", 
        "title", "subject", "creator", "keywords", "description", 
        "lastModifiedBy", "revision", "lastPrinted", "created", 
        "modified", "PresentationFormat", "Slides", "Notes", 
        "HiddenSlides", "MMClips", "category", "language", "HLinks"
    ]
    filtered_metadata = {k: v for k, v in metadata.items() if k in valid_columns and v is not None}

    cursor.execute("SELECT * FROM documentmetadata WHERE file_id = ?", (file_id,))
    row = cursor.fetchone()

    if row is None and filtered_metadata:
        columns = '", "'.join(filtered_metadata.keys())
        placeholders = ', '.join(['?'] * len(filtered_metadata))
        sql = f'INSERT INTO documentmetadata (file_id, filename, "{columns}") VALUES (?, ?, {placeholders})'
        values = [file_id, filename] + list(filtered_metadata.values())
        cursor.execute(sql, values)
    elif row:
        for key, value in filtered_metadata.items():
            if key not in row or row[key] is None:
                sql = f'UPDATE documentmetadata SET "{key}" = ? WHERE file_id = ?'
                cursor.execute(sql, (value, file_id))
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
                    save_metadata(conn, document_id,os.path.basename(file_path), metadata)
                extract_media_from_blob(document_id, blob_data, source_file_name, cursor, skipped_files)

    return skipped_files