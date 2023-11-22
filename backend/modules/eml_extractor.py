import email
from email.header import decode_header
import datetime
import hashlib
import re
from .ole_extractor import OLEExtractor
from .hwp_extractor import HWPExtractor
from .docx_extractor import DOCXExtractor
from .pptx_extractor import PPTXExtractor
from .xlsx_extractor import XLSXExtractor
from .pdf_extractor import PDFExtractor
import io

class EmlParser:
    def __init__(self, eml_data):
        self.eml_data = eml_data
        self.msg = None

    def parse_eml_data(self):
        self.msg = email.message_from_bytes(self.eml_data)

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
                
                # Word, PowerPoint, Excel, HWP 문서인 경우에만 내용을 해석
                if content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    docx_text = DOCXExtractor(body)
                    plain_text = docx_text.get_text()
                elif content_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                    # .pptx 파일인 경우 처리
                    pptx_text = PPTXExtractor(body)
                    plain_text = pptx_text.get_text()
                elif content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    # .xlsx 파일인 경우 처리
                    xlsx_text = XLSXExtractor(body)
                    plain_text = xlsx_text.get_text()
                elif content_type == 'application/x-hwp':
                    # .hwp 파일인 경우 처리
                    hwp_text = HWPExtractor(body)
                    plain_text = hwp_text.get_text()
                elif content_type in ['application/msword', 'application/vnd.ms-powerpoint', 'application/vnd.ms-excel']:
                    ole_text = OLEExtractor(body)
                    plain_text = ole_text.get_text()
                elif content_type == 'application/pdf':
                    # .pdf 파일인 경우 처리
                    pdf_text = PDFExtractor(body)
                    plain_text = pdf_text.get_text()
                else:
                    plain_text = None
                
                attachments.append((filename, content_type, body, plain_text))
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
        ctime = datetime.datetime.now()
        mtime = datetime.datetime.now()
        atime = datetime.datetime.now()
        ctime_str = ctime.strftime('%Y-%m-%d %H:%M:%S')
        mtime_str = mtime.strftime('%Y-%m-%d %H:%M:%S')
        atime_str = atime.strftime('%Y-%m-%d %H:%M:%S')
        return ctime_str, mtime_str, atime_str

    def calculate_hash(self, file_data):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_data)
        return sha256_hash.hexdigest()

    def process_eml(self):
        self.parse_eml_data()
        ctime, mtime, atime = self.parse_eml_dates()
        if self.msg['Subject']:
            subject = decode_header(self.msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8')
        else:
            subject = '제목 없음'
        date_str = self.msg['Date']
        date = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')

        # 'From' 필드 처리
        from_ = decode_header(self.msg['From'])[0][0]
        if isinstance(from_, bytes):
            from_ = from_.decode('utf-8')

        # ';'를 ','로 바꾸기
        from_ = from_.replace(';', ',')

        # 'From' 필드에서 원치 않는 문자 제거 (영문, 숫자, '@', '.', ',', '_', 한글 허용)
        from_ = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', from_)

        # 'To' 필드 처리
        to = decode_header(self.msg['To'])[0][0]
        if isinstance(to, bytes):
            to = to.decode('utf-8')
        to = to.replace('<', '').replace('>', '').strip()

        # ';'를 ','로 바꾸기
        to = to.replace(';', ',')

        # 'To' 필드에서 원치 않는 문자 제거 (영문, 숫자, '@', '.', ',', '_', 한글 허용)
        to = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', to)

        mail_body = self.extract_body()
        hash_value = self.calculate_hash(mail_body.encode())

        return subject, formatted_date, from_, to, ctime, mtime, atime, hash_value, mail_body

'''
if __name__ == "__main__":
    # EML 파일을 바이트 스트림으로 읽어옴
    with open(r"D:\\과제제출파일\\강대명 멘토\\eml_pst\\권순형 그에대해 알아보자.eml", "rb") as eml_file:
        eml_data = eml_file.read()

        # EML 데이터를 사용하여 EmlParser 인스턴스를 생성
        parser = EmlParser(eml_data)

        # EML 파일 정보 추출
        subject, date, from_, to, ctime, mtime, atime, hash_value, mail_body = parser.process_eml()
        attachments = parser.extract_attachments()

        # 추출한 정보 출력
        print("Subject:", subject)
        print("Date:", date)
        print("From:", from_)
        print("To:", to)
        print("Mail Body:", mail_body)
        print("Hash:", hash_value)

        if attachments:
            print("Attachments:")
            for filename, content_type, body, text_content in attachments:
                print("  Filename:", filename)
                print("  Content Type:", content_type)
                print("  Body:", body)
                print("  Text Content:", text_content)

'''
