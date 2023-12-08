import os
import sqlite3

class FileProcessor:
    def __init__(self, db_path):
        self.db_path = db_path

    def detect_file_extension(self, byte_stream):
        if b'\x70\x70\x74\x2F\x73\x6C\x69\x64\x65\x73\x2F\x73\x6C\x69\x64\x65\x31\x2E\x78\x6D\x6C' in byte_stream:
            return 'pptx'
        elif b'\x78\x6C\x2F\x77\x6F\x72\x6B\x73\x68\x65\x65\x74\x73\x2F\x73\x68\x65\x65\x74\x31\x2E\x78\x6D\x6C' in byte_stream:
            return 'xlsx'
        elif b'\x77\x6F\x72\x64\x2F\x64\x6F\x63\x75\x6D\x65\x6E\x74\x2E\x78\x6D\x6C' in byte_stream:
            return 'docx'
        elif b'\x48\x00\x77\x00\x70\x00\x53\x00\x75\x00\x6D\x00\x6D\x00\x61\x00\x72\x00\x79\x00\x49\x00\x6E\x00\x66\x00\x6F\x00\x72\x00\x6D\x00\x61\x00\x74\x00\x69\x00\x6F\x00\x6E' in byte_stream:
            return 'hwp'
        elif b'\x25\x40\x44\x46\x2D' in byte_stream:
            return 'pdf'
        else:
            return None

    def process_file(self):
        # 연결된 데이터베이스에 대한 커서 생성
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # files 테이블에서 모든 레코드를 가져옴
            cursor.execute("SELECT file_path, blob_data FROM files")
            rows = cursor.fetchall()

            for row in rows:
                file_path = row[0]
                byte_stream = row[1]

                # 파일 이름에서 확장자 추출
                file_extension = os.path.splitext(file_path)[1][1:]

                # 확장자 검출
                detected_extension = self.detect_file_extension(byte_stream)

                # 결과 출력 및 isMatch 업데이트
                if detected_extension:
                    if file_extension in detected_extension:
                        is_match = "일치"
                    else:
                        is_match = "불일치"
                else:
                    is_match = "파일 확장자를 결정할 수 없습니다."

                # isMatch 열 업데이트
                cursor.execute("UPDATE files SET isMatch = ? WHERE file_path = ?", (is_match, file_path))

            # 변경사항을 저장
            conn.commit()

        finally:
            # 데이터베이스 연결 해제
            conn.close()
    
    def process_file_emlAttachments(self):
        # 연결된 데이터베이스에 대한 커서 생성
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # files 테이블에서 모든 레코드를 가져옴
            cursor.execute("SELECT filename, data FROM emlAttachments")
            rows = cursor.fetchall()

            for row in rows:
                file_path = row[0]
                byte_stream = row[1]

                # 파일 이름에서 확장자 추출
                file_extension = os.path.splitext(file_path)[1][1:]

                # 확장자 검출
                detected_extension = self.detect_file_extension(byte_stream)

                # 결과 출력 및 isMatch 업데이트
                if detected_extension:
                    if file_extension in detected_extension:
                        is_match = "일치"
                    else:
                        is_match = "불일치"
                else:
                    is_match = "파일 확장자를 결정할 수 없습니다."

                # isMatch 열 업데이트
                cursor.execute("UPDATE emlAttachments SET isMatch = ? WHERE filename = ?", (is_match, file_path))

            # 변경사항을 저장
            conn.commit()

        finally:
            # 데이터베이스 연결 해제
            conn.close()
            
    def process_file_pstAttachments(self):
        # 연결된 데이터베이스에 대한 커서 생성
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # files 테이블에서 모든 레코드를 가져옴
            cursor.execute("SELECT filename, data FROM pstAttachments")
            rows = cursor.fetchall()

            for row in rows:
                file_path = row[0]
                byte_stream = row[1]

                # 파일 이름에서 확장자 추출
                file_extension = os.path.splitext(file_path)[1][1:]

                # 확장자 검출
                detected_extension = self.detect_file_extension(byte_stream)

                # 결과 출력 및 isMatch 업데이트
                if detected_extension:
                    if file_extension in detected_extension:
                        is_match = "일치"
                    else:
                        is_match = "불일치"
                else:
                    is_match = "파일 확장자를 결정할 수 없습니다."

                # isMatch 열 업데이트
                cursor.execute("UPDATE pstAttachments SET isMatch = ? WHERE filename = ?", (is_match, file_path))

            # 변경사항을 저장
            conn.commit()

        finally:
            # 데이터베이스 연결 해제
            conn.close()

# # 실행 코드
# db_path = r'D:\\new_TeamJSD\\Webtocpy\\cases\\성심당 사건23\\parsing.sqlite'
# file_processor = FileProcessor(db_path)
# file_processor.process_file()
# file_processor2 = FileProcessor(db_path)
# file_processor2.process_file_emlAttachments()
