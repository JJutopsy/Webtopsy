from flask import Flask, request, jsonify, Blueprint, make_response
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import sqlite3
import os

app = Flask(__name__)
similarity_bp = Blueprint('similarity', __name__)

# MeCab 객체 생성
mecab = MeCab.Tagger()

def tokenize_words(text):
    mecab = MeCab.Tagger()
    words = mecab.parse(text).split()
    words = [word.split('\t')[0] for word in words if 'NNG' in word or 'NNP' in word and len(word) > 1]
    return words

@similarity_bp.route('/similarity', methods=['POST'])
def similarity():
    data = request.json
    if not data or 'parsingDBpath' not in data or 'primary_id_key' not in data:
        return make_response(jsonify({'error': 'Missing data in request'}), 400)

    db_path = data['parsingDBpath']
    primary_id_key = data['primary_id_key']

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 기준 문서의 plain_text 및 hash_value 가져오기
        cursor.execute("SELECT plain_text, file_path, hash_value FROM files WHERE id=?", (primary_id_key,))
        result = cursor.fetchone()
        if not result:
            return make_response(jsonify({'error': 'Document not found'}), 404)
        
        text1, primary_file_path, primary_hash = result

        # 기준 문서를 동일 문서 목록에 추가
        identical_documents = [{
            'id': primary_id_key,
            'filename': os.path.basename(primary_file_path),
            'hash_value': primary_hash
        }]

        # 나머지 문서들 가져오기
        cursor.execute("SELECT id, plain_text, file_path, hash_value FROM files WHERE id != ?", (primary_id_key,))
        documents = cursor.fetchall()

        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
        similar_documents = []

        text1_nouns = ' '.join(tokenize_words(text1))

        for doc in documents:
            doc_id, doc_text, doc_filepath, doc_hash = doc
            doc_text_nouns = ' '.join(tokenize_words(doc_text))

            # 벡터화 및 유사도 계산
            tfidf_matrix = vectorizer.fit_transform([text1_nouns, doc_text_nouns])
            euclidean_dist = euclidean_distances(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = 1 - euclidean_dist[0][0]
            
            if similarity_score >= 0.97:
                similar_documents.append({
                    'id': doc_id,
                    'filename': os.path.basename(doc_filepath),
                    'similarity_score': similarity_score
                })

        return jsonify({
            'identical_documents': identical_documents,
            'similar_documents': similar_documents
        })

    except sqlite3.DatabaseError as e:
        return make_response(jsonify({'error': 'Database error: ' + str(e)}), 500)
    finally:
        if conn:
            conn.close()