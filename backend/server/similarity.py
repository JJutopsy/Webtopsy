from flask import Flask, request, jsonify, Blueprint, make_response
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import sqlite3
import os

app = Flask(__name__)
similarity_bp = Blueprint('similarity',__name__)

# MeCab 객체 생성
m = MeCab.Tagger()

def tokenize_words(text):
    m = MeCab.Tagger()
    words = m.parse(text).split()
    words = [word.split('\t')[0] for word in words if 'NNG' in word and len(word) > 1]
    return words

@similarity_bp.route('/similarity', methods=['POST'])
def similarity():
    data = request.json
    if not data or 'parsingDBpath' not in data or 'primary_id_key' not in data:
        return make_response(jsonify({'error': 'Missing data in request'}), 400)

    db_path = data['parsingDBpath']
    primary_id_key = data['primary_id_key']
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT plain_text, file_path FROM files WHERE id=?", (primary_id_key,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return make_response(jsonify({'error': 'Document not found'}), 404)
        text1, primary_file_path = result
        primary_extension = os.path.splitext(primary_file_path)[1]

        cursor.execute("SELECT id, plain_text, file_path FROM files WHERE file_path LIKE ?", ('%' + primary_extension,))
        documents = cursor.fetchall()

        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4), stop_words=None)
        similar_documents = []

        text1_nouns = ' '.join(tokenize_words(text1))

        for doc in documents:
            doc_id, doc_text, doc_filepath = doc
            doc_text_nouns = ' '.join(tokenize_words(doc_text))
            # 벡터화
            tfidf_matrix = vectorizer.fit_transform([text1_nouns, doc_text_nouns])
            # 유클리디언 거리 계산
            euclidean_dist = euclidean_distances(tfidf_matrix[0:1], tfidf_matrix[1:2])
            # 거리를 유사도 점수로 변환
            similarity_score = 1 - euclidean_dist[0][0]
            
            if similarity_score >= 0.97:
                similar_documents.append({
                    'id': doc_id,
                    'filename': os.path.basename(doc_filepath),
                    'similarity_percentage': similarity_score
                })
        return jsonify(similar_documents)

    except sqlite3.DatabaseError as e:
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        # 예외 발생 여부에 관계없이 데이터베이스 연결이 열려있는지 확인하고 닫기
        if conn is not None:
            conn.close()