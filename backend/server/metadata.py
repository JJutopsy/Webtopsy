import sqlite3
from lxml import etree
import zipfile
import io

# 네임스페이스 정의
namespaces = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dcterms': 'http://purl.org/dc/terms/',
    'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
}

# core.xml에서 메타데이터 추출
def extract_core_metadata(core_xml_root):
    metadata = {
        'Title': core_xml_root.findtext('.//dc:title', namespaces=namespaces),
        'Author': core_xml_root.findtext('.//dc:creator', namespaces=namespaces),
        'Subject': core_xml_root.findtext('.//dc:subject', namespaces=namespaces),
        'Keywords': core_xml_root.findtext('.//cp:keywords', namespaces=namespaces),
        'Description': core_xml_root.findtext('.//dc:description', namespaces=namespaces),
        'LastModifiedBy': core_xml_root.findtext('.//cp:lastModifiedBy', namespaces=namespaces),
        'ModificationDate': core_xml_root.findtext('.//dcterms:modified', namespaces=namespaces),
        'CreationDate': core_xml_root.findtext('.//dcterms:created', namespaces=namespaces),
        'LastPrintedDate': core_xml_root.findtext('.//cp:lastPrinted', namespaces=namespaces)
    }
    return metadata

# app.xml에서 메타데이터 추출
def extract_app_metadata(app_xml_root):
    metadata = {
        'ApplicationName': app_xml_root.findtext('.//ep:Application', namespaces=namespaces),
        'TotalTime': app_xml_root.findtext('.//ep:TotalTime', namespaces=namespaces),
        'Pages': app_xml_root.findtext('.//ep:Pages', namespaces=namespaces),
        'Words': app_xml_root.findtext('.//ep:Words', namespaces=namespaces),
        'Characters': app_xml_root.findtext('.//ep:Characters', namespaces=namespaces),
        'AppVersion': app_xml_root.findtext('.//ep:AppVersion', namespaces=namespaces)
    }
    return metadata

# 메타데이터를 데이터베이스에 저장하는 함수
def save_metadata_to_db(db_path, core_metadata, app_metadata, file_extension):
    # 데이터베이스 연결 및 커서 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # INSERT 쿼리 준비
    query = """
        INSERT INTO DocumentMetadata (
            Title, Author, Subject, Keywords, Description, LastModifiedBy,
            ModificationDate, CreationDate, LastPrintedDate,
            ApplicationName, TotalTime, Pages, Words, Characters, AppVersion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # 공통 메타데이터 및 확장자별 메타데이터 삽입 로직
    insert_data = (
        core_metadata.get('Title'),
        core_metadata.get('Author'),
        core_metadata.get('Subject'),
        core_metadata.get('Keywords'),
        core_metadata.get('Description'),
        core_metadata.get('LastModifiedBy'),
        core_metadata.get('ModificationDate'),
        core_metadata.get('CreationDate'),
        core_metadata.get('LastPrintedDate'),
        app_metadata.get('ApplicationName'),
        app_metadata.get('TotalTime'),
        app_metadata.get('Pages'),
        app_metadata.get('Words'),
        app_metadata.get('Characters'),
        app_metadata.get('AppVersion')
    )

    # INSERT 쿼리 실행
    cursor.execute(query, insert_data)

    # 변경사항 커밋 및 데이터베이스 연결 닫기
    conn.commit()
    conn.close()
    
def is_ooxml(blob_data):
    # OOXML 파일인지 확인하는 함수.
    try:
        with zipfile.ZipFile(io.BytesIO(blob_data), 'r') as zipped_file:
            return '[Content_Types].xml' in zipped_file.namelist()
    except zipfile.BadZipFile:
        return False

def main(db_path, primary_id_key):
    # 데이터베이스에서 파일 경로와 BLOB 데이터를 가져옴
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, blob_data, hash_value FROM files WHERE id = ?", (primary_id_key,))
    row = cursor.fetchone()
    conn.close()

    if row:
        file_path, blob_data, file_hash = row
        if is_ooxml(blob_data):
            # BLOB 데이터에서 OOXML 파일의 시그니처 확인 후 처리
            with zipfile.ZipFile(io.BytesIO(blob_data), 'r') as zipped_file:
                # core.xml과 app.xml 내용을 파싱
                if 'docProps/core.xml' in zipped_file.namelist() and 'docProps/app.xml' in zipped_file.namelist():
                    with zipped_file.open('docProps/core.xml') as f:
                        core_xml_content = f.read()
                    with zipped_file.open('docProps/app.xml') as f:
                        app_xml_content = f.read()
                    
                    # XML 파싱
                    core_xml_root = etree.fromstring(core_xml_content)
                    app_xml_root = etree.fromstring(app_xml_content)
                    
                    # 메타데이터 추출
                    core_metadata = extract_core_metadata(core_xml_root)
                    app_metadata = extract_app_metadata(app_xml_root)
                    
                    # 추출한 메타데이터를 데이터베이스에 저장
                    save_metadata_to_db(db_path, file_path, file_hash, core_metadata, app_metadata)
        else:
            print("Provided file is not an OOXML format.")

if __name__ == '__main__':
    main()