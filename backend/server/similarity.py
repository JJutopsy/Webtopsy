from flask import Flask, request, jsonify, Blueprint, make_response
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import os

app = Flask(__name__)
similarity_bp = Blueprint('similarity', __name__)

# MeCab 객체 생성
m = MeCab.Tagger()

def tokenize_words(text):
    m = MeCab.Tagger()
    words = m.parse(text).split()
    words = [word.split('\t')[0] for word in words if 'NNG' in word and len(word) > 1]
    return words

@similarity_bp.route('/', methods=['POST'])
def similarity():
    data = request.json
    if not data or 'parsingDBpath' not in data or 'primary_id_key' not in data:
        return make_response(jsonify({'error': 'Missing data in request'}), 400)

    db_path = data['parsingDBpath']
    primary_id_key = data['primary_id_key']

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

            tfidf_matrix = vectorizer.fit_transform([text1_nouns, doc_text_nouns])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

            similarity_percentage = round(cosine_sim[0][0] * 100, 2)
            if cosine_sim[0][0] >= 0.8:
                similar_documents.append({
                    'id': doc_id,
                    'filename': os.path.basename(doc_filepath),
                    'similarity_percentage': similarity_percentage
                })

        conn.close()
        return jsonify(similar_documents)

    except sqlite3.DatabaseError as e:
        conn.close()
        return make_response(jsonify({'error': str(e)}), 500)
