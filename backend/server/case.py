from flask import Blueprint, jsonify
import sqlite3

case_bp = Blueprint('case', __name__)

@case_bp.route('/case', methods=['GET'])
def get_case_data():
    try:
        conn = sqlite3.connect('casedb.sqlite')
        cursor = conn.cursor()

        # 데이터베이스에서 정보 조회
        cursor.execute("SELECT * FROM cases")
        rows = cursor.fetchall()
        # JSON 형태로 변환
        case_data = []
        for row in rows:
            case = {
                'id': row[0],
                'casename': row[1],
                'caseinfo': row[2],
                'username': row[3], 
                'parsingDBpath': row[4]
                # 필요한 경우 데이터베이스 컬럼에 맞게 추가
            }
            case_data.append(case)

        conn.close()

        return jsonify({'cases': case_data})

    except Exception as e:
        return jsonify({'error': str(e)})
