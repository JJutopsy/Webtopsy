import sqlite3
import re

class EmlPersonUpdater:
    def __init__(self, db_path):
        self.db_path = db_path

    def process_contact(self, contact):
        contact = contact.replace(';', ',')
        contact = re.sub(r'[^가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z0-9@.,_]', '', contact)
        return contact

    def update_eml_person_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DROP TABLE IF EXISTS emlPerson')
            cursor.execute('''
                CREATE TABLE emlPerson (
                    emlPerson TEXT,
                    relatedPerson TEXT,
                    seCount INTEGER,
                    reCount INTEGER
                )
            ''')

            cursor.execute('''
                SELECT DISTINCT sender FROM emlEmails
                UNION
                SELECT DISTINCT receiver FROM emlEmails
            ''')
            unique_contacts = cursor.fetchall()

            for contact in unique_contacts:
                processed_contact = self.process_contact(contact[0])
                contacts_list = processed_contact.split(',')

                for individual_contact in set(contacts_list):
                    related_persons = set()  # 중복 방지를 위해 집합(set) 사용

                    cursor.execute('''
                        SELECT DISTINCT sender, receiver FROM emlEmails
                        WHERE sender = ? OR receiver LIKE ?
                    ''', (individual_contact, f'%{individual_contact}%'))
                    email_contacts = cursor.fetchall()

                    for email_contact in email_contacts:
                        if email_contact[0] == individual_contact:
                            related_persons.add(self.process_contact(email_contact[1]))
                        else:
                            related_persons.add(self.process_contact(email_contact[0]))

                    related_person_str = ','.join(related_persons)

                    # relatedPerson 열에서 중복 제거
                    related_person_str = ','.join(list(set(related_person_str.split(','))))

                    # sender 및 receiver 열에서 연락처의 출현 횟수 계산
                    se_count = cursor.execute('''
                        SELECT COUNT(*) FROM emlEmails
                        WHERE sender = ?
                    ''', (individual_contact,)).fetchone()[0]

                    re_count = cursor.execute('''
                        SELECT COUNT(*) FROM emlEmails
                        WHERE receiver = ? OR receiver LIKE ?
                    ''', (individual_contact, f'%{individual_contact}%')).fetchone()[0]

                    cursor.execute('''
                        INSERT INTO emlPerson (emlPerson, relatedPerson, seCount, reCount) VALUES (?, ?, ?, ?)
                    ''', (individual_contact, related_person_str, se_count, re_count))

            cursor.execute('''
                CREATE TABLE emlPerson_temp AS
                SELECT emlPerson, GROUP_CONCAT(DISTINCT relatedPerson) AS relatedPerson, seCount, reCount
                FROM emlPerson
                GROUP BY emlPerson
            ''')

            cursor.execute('DROP TABLE IF EXISTS emlPerson')
            cursor.execute('ALTER TABLE emlPerson_temp RENAME TO emlPerson')

            conn.commit()

        except sqlite3.Error as e:
            print("SQLite 오류:", e)

        finally:
            conn.close()

# 예시 사용법
# db_path = r'D:\\Download\\Webtopsy-main\\Webtopsy-main\\cases\\성심당 사건16\\parsing.sqlite'
# eml_person_updater = EmlPersonUpdater(db_path)
# eml_person_updater.update_eml_person_table()
