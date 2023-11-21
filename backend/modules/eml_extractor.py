import os
import email
from email.header import decode_header
import datetime
import hashlib
import sqlite3

class EmlExtractor:
    def __init__(self, eml_file_path, save_dir=None):
        self.eml_file_path = eml_file_path
        self.save_dir = save_dir
        self.msg = None

    def parse_eml_file(self):
        with open(self.eml_file_path, 'rb') as eml_file:
            self.msg = email.message_from_binary_file(eml_file)

    def extract_attachments(self):
        attachments = []
        for part in self.msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode('utf-8')
                content_type = part.get_content_type()
                body = part.get_payload(decode=True)
                attachments.append((filename, content_type, body))
        return attachments

    def extract_body(self):
        body = ""
        if self.msg.is_multipart():
            for part in self.msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = self.msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return body

    def parse_eml_dates(self):
        ctime = os.path.getctime(self.eml_file_path)
        mtime = os.path.getmtime(self.eml_file_path)
        atime = os.path.getatime(self.eml_file_path)
        ctime_str = datetime.datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        atime_str = datetime.datetime.fromtimestamp(atime).strftime('%Y-%m-%d %H:%M:%S')
        return ctime_str, mtime_str, atime_str

    def connect_to_database(self, db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        return conn, cursor

    def create_database_table(self, cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emlAttachments (
                filename TEXT,
                filepath TEXT,
                hash TEXT,
                data BLOB
            )
        """)

    def add_attachment_to_database(self, db_name, filename, filepath, hash, data):
        allowed_extensions = ['.doc', '.docx', '.xlsx', '.pdf', '.ppt', '.pptx']
        if any(filename.lower().endswith(ext) for ext in allowed_extensions):
            conn, cursor = self.connect_to_database(db_name)
            cursor.execute("INSERT INTO emlAttachments (filename, filepath, hash, data) VALUES (?, ?, ?, ?)",
                           (filename, filepath, hash, data))
            conn.commit()
            conn.close()

    def process_eml(self):
        self.parse_eml_file()
        ctime, mtime, atime = self.parse_eml_dates()
        subject = decode_header(self.msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8')
        date = self.msg['Date']
        from_ = decode_header(self.msg['From'])[0][0]
        if isinstance(from_, bytes):
            from_ = from_.decode('utf-8')
        to = decode_header(self.msg['To'])[0][0]
        if isinstance(to, bytes):
            to = to.decode('utf-8')
        to = to.replace('<', '').replace('>', '').strip()
        mail_body = self.extract_body()
        eml_filename = os.path.basename(self.eml_file_path)
        md5_hash = hashlib.md5(mail_body.encode()).hexdigest()

        if self.save_dir:
            os.makedirs(self.save_dir, exist_ok=True)
            save_location = os.path.join(self.save_dir, eml_filename)
        else:
            save_location = self.eml_file_path

        db_file_path = os.path.join(self.save_dir, 'parsing.db')

        conn, cursor = self.connect_to_database(db_file_path)
        self.create_database_table(cursor)
        conn.commit()
        conn.close()

        if self.save_dir:
            for filename, content_type, body in self.extract_attachments():
                data = sqlite3.Binary(body)
                self.add_attachment_to_database(db_file_path, filename, self.eml_file_path, hashlib.md5(body).hexdigest(), data)

        return subject, date, from_, to, ctime, mtime, atime, eml_filename, save_location, md5_hash, mail_body

    def create_and_insert_to_database(self):
        try:
            subject, date, from_, to, ctime, mtime, atime, eml_filename, save_location, md5_hash, mail_body = self.process_eml()
            conn = sqlite3.connect(os.path.join(self.save_dir, 'parsing.db'))
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emlEmails (
                    eml_filename TEXT,
                    save_location TEXT,
                    md5_hash TEXT,
                    subject TEXT,
                    date TEXT,
                    sender TEXT,
                    receiver TEXT,
                    ctime TEXT,
                    mtime TEXT,
                    atime TEXT,
                    mail_body Text
                )
            ''')
             
            cursor.execute('''
                INSERT INTO emlEmails (eml_filename, save_location, md5_hash, subject, date, sender, receiver, ctime, mtime, atime, mail_body )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (eml_filename, save_location, md5_hash, subject, date, from_, to, ctime, mtime, atime, mail_body))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred: {e}")


'''
if __name__ == "__main__":
    eml_file_path = r"D:\\과제제출파일\\강대명 멘토\\eml_pst\\권순형 그에대해 알아보자.eml"  # EML 파일 경로
    save_dir = r"D:\\과제제출파일\\강대명 멘토\\eml_pst"  # 데이터베이스 및 첨부 파일을 저장할 디렉토리

    eml_parser = EmlParser(eml_file_path, save_dir)

    # EML 파일 파싱 및 데이터베이스 저장
    eml_parser.create_and_insert_to_database()

    print("EML 파일 파싱 및 데이터베이스 저장이 완료되었습니다.")
'''

