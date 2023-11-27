import os
import win32com.client
import re
import hashlib
import tempfile
import pythoncom
import datetime

class PSTParser:
    def __init__(self, pst_data):
        self.pst_data = pst_data

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', '', filename)

    @staticmethod
    def calculate_md5(content):
        md5_hash = hashlib.md5(content).hexdigest()
        return md5_hash
    
    def calculate_hash(self, file_data):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_data.encode('utf-8'))
        return sha256_hash.hexdigest()

    def process_folder(self, folder):
        emails = []
        for item in folder.Items:
            if item.Class == 43:  # 43은 이메일 아이템
                try:
                    subject = self.sanitize_filename(item.Subject)
                    
                    # Process sender
                    sender = item.SenderName
                    sender = sender.replace(';', ',')
                    sender = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', sender)

                    # Process receiver
                    receiver = item.To
                    receiver = receiver.replace(';', ',')
                    receiver = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', receiver)

                    body = item.Body
                    date = item.ReceivedTime
                    date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)

                    # Extract additional timestamps
                    ctime = item.CreationTime
                    mtime = item.LastModificationTime
                    atime = getattr(item, 'LastAccessTime', None)

                    ctime = datetime.datetime(ctime.year, ctime.month, ctime.day, ctime.hour, ctime.minute, ctime.second) if ctime else None
                    mtime = datetime.datetime(mtime.year, mtime.month, mtime.day, mtime.hour, mtime.minute, mtime.second) if mtime else None
                    atime = datetime.datetime(atime.year, atime.month, atime.day, atime.hour, atime.minute, atime.second) if atime else None

                    emails.append({
                        'subject': subject,
                        'sender': sender,
                        'receiver': receiver,
                        'body': body,
                        'date': date,
                        'ctime': ctime,
                        'mtime': mtime,
                        'atime': atime,
                    })

                except Exception as e:
                    print(f"예기치 않은 오류가 발생했습니다: {e}")

        for subfolder in folder.Folders:
            emails.extend(self.process_folder(subfolder))

        return emails

    def extract_emails_from_pst(self):
        # Initialize the COM library
        pythoncom.CoInitialize()

        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        pst_path = tempfile.mktemp(suffix='.pst')

        with open(pst_path, 'wb') as pst_file:
            pst_file.write(self.pst_data)

        outlook.AddStore(pst_path)
        root_folder = outlook.Folders.GetLast()

        emails = self.process_folder(root_folder)

        # Uninitialize the COM library when done
        pythoncom.CoUninitialize()

        temp_pst_path = os.path.join(tempfile.gettempdir(), 'temp.pst')
        if os.path.exists(temp_pst_path):
            os.remove(temp_pst_path)

        return emails



'''
# PST 파일을 읽어 바이트 스트림으로 변환
pst_file_path = r'D:\\과제제출파일\\강대명 멘토\\eml_pst\\백업JISOOLEE.pst'
with open(pst_file_path, 'rb') as pst_file:
    pst_data = pst_file.read()

parser = PSTParser(pst_data)
emails = parser.extract_emails_from_pst()

for email in emails:
    print(email)
'''



