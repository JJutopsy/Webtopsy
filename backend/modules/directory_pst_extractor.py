import os
import win32com.client
import re
import sqlite3
import hashlib
import pythoncom
import time
from .ole_extractor import OLEExtractor
from .hwp_extractor import HWPExtractor
from .docx_extractor import DOCXExtractor
from .pptx_extractor import PPTXExtractor
from .xlsx_extractor import XLSXExtractor
from .pdf_extractor import PDFExtractor


class PSTParser:
    def __init__(self, pst_data, save_dir):
        self.pst_data = pst_data
        self.save_dir = save_dir

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', '', filename)

    @staticmethod
    def is_allowed_attachment(filename):
        allowed_extensions = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xlsx", ".eml"]
        _, file_extension = os.path.splitext(filename)
        return file_extension.lower() in allowed_extensions

    @staticmethod
    def calculate_hash(file_data):
        if isinstance(file_data, str):
            file_data = file_data.encode('utf-8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_data)
        return sha256_hash.hexdigest()

    def create_email_table(self, connection):
        cursor = connection.cursor()
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
                blob_data BLOB,
                tag TEXT,
                NNP TEXT
            )
        ''')
        connection.commit()

    def create_attachment_table(self, connection):
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pstAttachments (
                save_location TEXT,
                subject TEXT,
                filename TEXT,
                hash TEXT,
                data BLOB,
                plain_text TEXT,
                isMatch TEXT,
                tag TEXT,
                NNP TEXT
            )
        ''')
        connection.commit()

    def save_email_to_database(self, connection, save_location, subject, date, sender, receiver, body, ctime, mtime, atime):
        try:
            date_str = date.strftime('%Y-%m-%d %H:%M:%S') if date else None

            ctime_str = ctime.strftime('%Y-%m-%d %H:%M:%S') if ctime else None
            mtime_str = mtime.strftime('%Y-%m-%d %H:%M:%S') if mtime else None
            atime_str = atime.strftime('%Y-%m-%d %H:%M:%S') if atime else None
            
            body_sha256 = self.calculate_hash(body)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO emlEmails (save_location, subject, date, sender, receiver, ctime, mtime, atime, hash, body)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (save_location, subject, date_str, sender, receiver, ctime_str, mtime_str, atime_str, body_sha256, body))
            connection.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")


    def save_attachment_to_database(self, connection, save_location, filename, content, plain_text, subject):
        hash = self.calculate_hash(content)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO pstAttachments (save_location, subject, filename, hash, data, plain_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (save_location, subject, filename, hash, content, plain_text))
        connection.commit()

    def wait_for_file_closure(self, file_path, max_attempts=10, wait_time=1):
        attempts = 0
        while attempts < max_attempts:
            try:
                with open(file_path, 'wb'):
                    return  # 파일이 열리지 않는 경우에만 여기로 이동
            except Exception as e:
                attempts += 1
                time.sleep(wait_time)

        raise Exception(f"Could not access file: {file_path}")

    
    def get_content_type(filename):
        _, file_extension = os.path.splitext(filename.lower())
        if file_extension == ".docx":
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_extension == ".pptx":
            return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif file_extension == ".xlsx":
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_extension == ".hwp":
            return 'application/x-hwp'
        elif file_extension in ['.doc', '.ppt', '.xls']:
            return 'application/msword'
        elif file_extension == ".pdf":
            return 'application/pdf'
        else:
            return None
    
    def process_folder(self, folder, connection, save_location):
        for item in folder.Items:
            if item.Class == 43:  # 43은 메일 아이템
                try:
                    subject = self.sanitize_filename(item.Subject)
                    
                    # 발신자 처리
                    sender = item.SenderName
                    sender = sender.replace(';', ',')
                    sender = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', sender)

                    # 수신자 처리
                    receiver = item.To
                    receiver = receiver.replace(';', ',')
                    receiver = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', receiver)

                    body = item.Body
                    date = item.ReceivedTime
                    ctime = item.CreationTime
                    mtime = item.LastModificationTime
                    atime = getattr(item, 'LastAccessTime', None)  # 속성이 없는 경우 None으로 설정
                    
                    self.save_email_to_database(connection, save_location, subject, date, sender, receiver, body, ctime, mtime, atime)

                    attachments = item.Attachments
                    for attachment in attachments:
                        filename = self.sanitize_filename(attachment.FileName)
                        if self.is_allowed_attachment(filename):
                            content_type = PSTParser.get_content_type(filename)
                            if content_type:
                                content = attachment.PropertyAccessor.GetProperty("http://schemas.microsoft.com/mapi/proptag/0x37010102")
                                
                                if content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                                    docx_text = DOCXExtractor(content)
                                    plain_text = docx_text.get_text()
                                elif content_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                                    pptx_text = PPTXExtractor(content)
                                    plain_text = pptx_text.get_text()
                                elif content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                                    xlsx_text = XLSXExtractor(content)
                                    plain_text = xlsx_text.get_text()
                                elif content_type == 'application/x-hwp':
                                    hwp_text = HWPExtractor(content)
                                    plain_text = hwp_text.get_text()
                                elif content_type in ['application/msword', 'application/vnd.ms-powerpoint', 'application/vnd.ms-excel']:
                                    ole_text = OLEExtractor(content)
                                    plain_text = ole_text.get_text()
                                elif content_type == 'application/pdf':
                                    pdf_text = PDFExtractor(content)
                                    plain_text = pdf_text.get_text()
                                else:
                                    plain_text = None

                                self.save_attachment_to_database(connection, save_location, filename, content, plain_text, subject)


                except Exception as e:
                    print(f"예기치 않은 오류가 발생했습니다: {e}")

        for subfolder in folder.Folders:
            self.process_folder(subfolder, connection, save_location)

    def extract_emails_from_pst(self, conn):
        try:
            pythoncom.CoInitialize()

            self.create_email_table(conn)
            self.create_attachment_table(conn)

            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            pst_path = os.path.join(self.save_dir, 'temp.pst')

            self.wait_for_file_closure(pst_path)
            with open(pst_path, 'wb') as pst_file:
                pst_file.write(self.pst_data)

            outlook.AddStore(pst_path)
            root_folder = outlook.Folders.GetLast()

            self.process_folder(root_folder, conn, os.path.dirname(pst_path))

            conn.close()

            temp_pst_path = os.path.join(self.save_dir, 'temp.pst')
            if os.path.exists(temp_pst_path):
                os.remove(temp_pst_path)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        finally:
            pythoncom.CoUninitialize()
