import sqlite3
import json

class EmailSearcher:
    def __init__(self, db_path, name, related_person):
        self.db_path = db_path
        self.name = name
        self.related_person = related_person

    def sort_and_print_related_emails(self):
        # SQLite 데이터베이스 연결
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # emlEmails 테이블에서 date 컬럼을 오름차순으로 정렬하여 데이터 가져오기
            query = f'''
                SELECT e.subject, strftime('%Y-%m-%d %H:%M:%S', e.date) as formatted_date,
                    e.sender, e.receiver, e.body, 
                    CASE
                        WHEN e.save_location LIKE '%.eml%' THEN (SELECT a_eml.filename FROM emlAttachments a_eml WHERE a_eml.save_location = e.save_location LIMIT 1)
                        WHEN e.save_location NOT LIKE '%.%' THEN (SELECT a_pst.filename FROM pstAttachments a_pst WHERE a_pst.subject = e.subject LIMIT 1)
                        ELSE NULL
                    END as attachment_filename
                FROM emlEmails e
                WHERE (e.sender LIKE '%' || ? || '%' OR e.receiver LIKE '%' || ? || '%')
                    AND (e.sender LIKE '%' || ? || '%' OR e.receiver LIKE '%' || ? || '%')
                ORDER BY formatted_date ASC
            '''
            cursor.execute(query, (self.name, self.name, self.related_person, self.related_person))

            # 데이터를 가져와서 각 이메일에 대해 JSON 형식으로 출력
            emails = cursor.fetchall()

            # 추가된 디버깅 출력
            print("검색 조건:", self.name, self.related_person)
            print("찾은 이메일 수:", len(emails))

            json_data = []
            for email in emails:
                subject, date, sender, receiver, body, attachment_filename = email
                email_data = {
                    "Subject": subject,
                    "Date": date,
                    "Sender": sender,
                    "Receiver": receiver,
                    "Body": body,
                    "Attachment": attachment_filename  # 첨부파일 정보 추가
                }
                json_data.append(email_data)

            # JSON 형식으로 출력
            return json_data

        except sqlite3.Error as e:
            print("SQLite 오류:", e)

        finally:
            # 연결 종료
            conn.close()

# 예시 사용법
# database_path = r'D:\\Download\\Webtopsy-main\\Webtopsy-main\\cases\\성심당 사건16\\parsing.sqlite'
# emlperson = '유광재'  # 여기에 찾고자 하는 이름을 넣어주세요.
# related_person = '이지수'  # 여기에 관계자의 이름을 넣어주세요.

# email_searcher = EmailSearcher(database_path, emlperson, related_person)
# email_searcher.sort_and_print_related_emails()
