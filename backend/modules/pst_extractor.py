import os
import win32com.client
import re
import sqlite3
import hashlib

class PSTExtractor:
    def __init__(self, pst_file_path, save_dir):
        self.pst_file_path = pst_file_path
        self.save_dir = save_dir

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', '', filename)

    @staticmethod
    def is_allowed_attachment(filename):
        allowed_extensions = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xlsx"]
        _, file_extension = os.path.splitext(filename)
        return file_extension.lower() in allowed_extensions

    @staticmethod
    def calculate_md5(content):
        md5_hash = hashlib.md5(content).hexdigest()
        return md5_hash

    def create_email_table(self, connection):
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pstEmails (
                pst_file_path TEXT,
                subject TEXT,
                sender TEXT,
                receiver TEXT,
                body_md5 TEXT,
                body TEXT
            )
        ''')
        connection.commit()

    def create_attachment_table(self, connection):
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pstAttachments (
                pst_file_path TEXT,
                filename TEXT,
                md5_hash TEXT,
                content BLOB
            )
        ''')
        connection.commit()

    def save_email_to_database(self, connection, subject, sender, receiver, body):
        body_md5 = self.calculate_md5(body.encode('utf-8'))
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO pstEmails (pst_file_path, subject, sender, receiver, body_md5, body)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.pst_file_path, subject, sender, receiver, body_md5, body))
        connection.commit()

    def save_attachment_to_database(self, connection, filename, content):
        md5_hash = self.calculate_md5(content)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO pstAttachments (pst_file_path, filename, md5_hash, content)
            VALUES (?, ?, ?, ?)
        ''', (self.pst_file_path, filename, md5_hash, content))
        connection.commit()

    def process_folder(self, folder, connection):
        for item in folder.Items:
            if item.Class == 43:  # 43은 메일 아이템
                try:
                    subject = self.sanitize_filename(item.Subject)
                    sender = item.SenderName
                    receiver = item.To
                    body = item.Body

                    self.save_email_to_database(connection, subject, sender, receiver, body)

                    attachments = item.Attachments
                    for attachment in attachments:
                        filename = self.sanitize_filename(attachment.FileName)
                        if self.is_allowed_attachment(filename):
                            content = attachment.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x37010102")
                            self.save_attachment_to_database(connection, filename, content)

                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

        for subfolder in folder.Folders:
            self.process_folder(subfolder, connection)

    def extract_emails_from_pst(self):
        db_file_path = os.path.join(self.save_dir, 'parsing.sqlite')
        connection = sqlite3.connect(db_file_path)
        self.create_email_table(connection)
        self.create_attachment_table(connection)

        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        outlook.AddStore(self.pst_file_path)
        root_folder = outlook.Folders.GetLast()

        self.process_folder(root_folder, connection)

        connection.close()

'''
if __name__ == "__main__":
    pst_file_path = r"D:\\과제제출파일\\강대명 멘토\\eml_pst\\백업JISOOLEE.pst"  # PST 파일 경로
    save_dir = r"D:\\과제제출파일\\강대명 멘토\\eml_pst"  # 데이터베이스 및 첨부 파일을 저장할 디렉토리

    pst_parser = PSTParser(pst_file_path, save_dir)

    # PST 파일에서 이메일 및 첨부 파일 추출 및 데이터베이스 저장
    pst_parser.extract_emails_from_pst()

    print("PST 파일에서 이메일 및 첨부 파일 추출 및 데이터베이스 저장이 완료되었습니다.")
'''

