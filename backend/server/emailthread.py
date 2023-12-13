from flask import Blueprint, request, jsonify
import sqlite3
from email.parser import BytesParser
from email import policy
import base64

emlthread_bp = Blueprint('emlthread', __name__)

@emlthread_bp.route('/emlthread', methods=['POST'])
def emlthread():
    data = request.json
    db_path = data.get('db_path')
    get_subject = data.get('email_subject')

    if not db_path or not get_subject:
        return jsonify({"error": "Database path and email subject are required"}), 400

    email_reader = EmailDatabaseReader(db_path)
    email_info = email_reader.get_email_info(get_subject)
    email_reader.close_connection()

    if email_info:
        return jsonify({"related_emails": email_info})
    else:
        return jsonify({"error": "No related emails found"}), 404
    
class EmailDatabaseReader:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def close_connection(self):
        self.conn.close()
        
    def get_email_info(self, get_subject):
        query = "SELECT blob_data FROM emlEmails WHERE subject = ?"
        self.cursor.execute(query, (get_subject,))
        result = self.cursor.fetchone()

        if result:
            blob_data = result[0]

            # NULL 값이 있는 경우 처리
            if blob_data is None:
                print("이메일에 blob_data가 없습니다.")
                return None

            msg = BytesParser(policy=policy.default).parsebytes(blob_data)

            # Message-ID, References, In-Reply-To 값 확인
            message_id = msg.get("Message-ID")
            references = msg.get("References", "").split()
            in_reply_to = msg.get("In-Reply-To", "").split()

            # 모든 관련 이메일 찾기
            related_emails = self.find_related_emails(message_id, references, in_reply_to)
            return related_emails
        else:
            print("주어진 제목을 가진 이메일이 없습니다.")
            return None

    def find_related_emails(self, message_id, references, in_reply_to):
        found_emails = []
        seen_message_ids = set()

        query = "SELECT subject, sender, receiver, date, body, blob_data FROM emlEmails"
        for row in self.cursor.execute(query):
            subject, sender, receiver, date, body, blob_data = row

            if body is None or blob_data is None:
                continue

            # blob_data에서 이메일 정보 파싱
            msg = BytesParser(policy=policy.default).parsebytes(blob_data)
            other_message_id = msg.get("Message-ID")
            other_references = msg.get("References", "").split()
            other_in_reply_to = msg.get("In-Reply-To", "").split()

            # 중복 제거 및 관련 이메일 확인
            if other_message_id not in seen_message_ids and \
               (other_message_id == message_id or \
               other_message_id in references or \
               other_message_id in in_reply_to or \
               any(ref in other_references or ref in other_in_reply_to for ref in references + in_reply_to)):
                seen_message_ids.add(other_message_id)
                email_data = {
                    "date": date,
                    "subject": subject,
                    "sender": sender,
                    "receiver": receiver,
                    "body": body
                }
                found_emails.append(email_data)

        # 각 이메일에 대한 첨부파일 정보 추가
        for email in found_emails:
            self.add_attachment_data(email['subject'], email)

        return sorted(found_emails, key=lambda x: x['date'])

    def add_attachment_data(self, subject, email):
        attachment_query = "SELECT filename, data FROM emlAttachments WHERE subject = ?"
        self.cursor.execute(attachment_query, (subject,))
        attachment_row = self.cursor.fetchone()

        if attachment_row:
            email['att_file_name'], att_file_data = attachment_row
            email['att_file_data'] = base64.b64encode(att_file_data).decode() if att_file_data else ""
        else:
            email['att_file_name'] = ""
            email['att_file_data'] = ""