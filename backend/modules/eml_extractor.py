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
from dateutil import parser as date_parser

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
                    #filename = filename.decode('utf-8')
                    try:
                        filename = filename.decode('utf-8')
                    except UnicodeDecodeError:
                        filename = filename.decode('euc-kr', errors='ignore')
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

        # Subject 처리
        if self.msg['Subject']:
            subject = decode_header(self.msg['Subject'])[0][0]
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode('utf-8')
                except UnicodeDecodeError:
                    subject = subject.decode('euc-kr', errors='ignore')
        else:
            subject = '제목 없음'

        # Date 처리
        date_str = self.msg.get('Date', '')
        formatted_date = '날짜 없음'  # 기본값 설정
        if date_str:
            try:
                # 타임존 정보 제거 후 날짜 파싱 시도
                date_str = re.sub(r'\([^)]*\)', '', date_str).strip()
                date = date_parser.parse(date_str)
                formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"날짜 파싱 오류 (스킵됨): {e}")
                return None  # 파싱 오류 발생 시, 이 이메일은 처리하지 않음

        # From 처리
        from_ = decode_header(self.msg['From'])[0][0]
        if isinstance(from_, bytes):
            try:
                from_ = from_.decode('utf-8')
            except UnicodeDecodeError:
                from_ = from_.decode('euc-kr', errors='ignore')
        from_ = from_.replace(';', ',')
        from_ = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', from_)

        # To 처리
        to = decode_header(self.msg['To'])[0][0]
        if isinstance(to, bytes):
            try:
                to = to.decode('utf-8')
            except UnicodeDecodeError:
                to = to.decode('euc-kr', errors='ignore')
        to = to.replace('<', '').replace('>', '').strip()
        to = to.replace(';', ',')
        to = re.sub(r'[^A-Za-z0-9@.,_가-힣]', '', to)

        # 메일 본문 추출
        mail_body = self.extract_body()

        # 해시 계산
        hash_value = self.calculate_hash(mail_body.encode())

        return subject, formatted_date, from_, to, ctime, mtime, atime, hash_value, mail_body


'''
if __name__ == "__main__":
    # EML 파일을 바이트 스트림으로 읽어옴
    with open(r"C:\\Users\\ksh88\\OneDrive\\문서\\카카오톡 받은 파일\\FW_ ORD11.089.w3x_230914\\FW_ ORD11.089.w3x_230914\\20170511_11991_제7기 IP 마이스터프로그램 모집공고(~6_9).eml", "rb") as eml_file:
        eml_data = eml_file.read()

        # EML 데이터를 사용하여 EmlParser 인스턴스를 생성
        parser = EmlParser(eml_data)

        # EML 파일 정보 추출
        subject, date, from_, to, ctime, mtime, atime, hash_value, mail_body = parser.process_eml()
        #attachments = parser.extract_attachments()

        # 추출한 정보 출력
        print("Subject:", subject)
        print("Date:", date)
        print("From:", from_)
        print("To:", to)
        print("Mail Body:", mail_body)
        print("Hash:", hash_value)

        # if attachments:
        #     print("Attachments:")
        #     for filename, content_type, body, text_content in attachments:
        #         print("  Filename:", filename)
        #         print("  Content Type:", content_type)
        #         print("  Body:", body)
        #         print("  Text Content:", text_content)
'''

