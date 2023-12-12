from flask import Blueprint, request, jsonify
import os
import sqlite3
from collections import Counter

# Define a Blueprint
dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route('/extension_distribution', methods=['POST'])
def get_extension_distribution():
    # Use request.json to get the JSON data sent in the POST request
    data = request.json
    db_path = data.get('db_path')
    if not db_path:
        return jsonify({"error": "Missing 'db_path' parameter"}), 400

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT file_path FROM files")

    # Extract extensions using os.path.splitext
    extensions = Counter(os.path.splitext(row[0])[1][1:] for row in cursor.fetchall())

    connection.close()

    # Convert the result to the desired format
    result = [{'name': ext, 'count': count} for ext, count in extensions.items()]

    # Sort the result by count in descending order
    sorted_result = sorted(result, key=lambda x: x['count'], reverse=True)
    
    return jsonify(sorted_result)


@dashboard_bp.route('/frequent_entities', methods=['POST'])
def get_frequent_entities():
    # Use request.json to get the JSON data sent in the POST request
    data = request.json
    db_path = data.get('db_path')

    if not db_path:
        return jsonify({"error": "Missing 'db_path' parameter"}), 400

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT NNP, tag FROM files")
    data = cursor.fetchall()

    people_tokens = get_tokens_by_category(data, "_인명")
    org_tokens = get_tokens_by_category(data, "_기관명")
    loc_tokens = get_tokens_by_category(data, "_지명")
    tag_tokens = get_tag_tokens(data)

    processed_people_data = get_most_common_tokens(people_tokens, 10)
    processed_org_data = get_most_common_tokens(org_tokens, 10)
    processed_loc_data = get_most_common_tokens(loc_tokens, 10)
    processed_tag_data = get_most_common_tags(tag_tokens, 10)

    connection.close()

    return jsonify({
        "processed_people_data": processed_people_data,
        "processed_org_data": processed_org_data,
        "processed_loc_data": processed_loc_data,
        "processed_tag_data": processed_tag_data
    })

def get_tokens_by_category(data, category):
    tokens = [entry_token.split('_')[0] for entry in data if entry and isinstance(entry, tuple) and entry[0] and category in entry[0] for entry_token in entry[0].split(',')]
    return tokens

def get_tag_tokens(data):
    tag_strings = [entry[1] for entry in data if entry and isinstance(entry, tuple) and entry[1] is not None]
    tag_tokens = [tag.strip() for string in tag_strings for tag in string.split(',') if tag]
    return tag_tokens

def get_most_common_tokens(tokens, count):
    counter_tokens = Counter(tokens)
    processed_data = [{"name": name, "count": count} for name, count in counter_tokens.most_common(count) if name]
    return processed_data

def get_most_common_tags(tags, count):
    counter_tags = Counter(tags)
    processed_data = [{"tag": tag, "count": count} for tag, count in counter_tags.most_common(count)]
    return processed_data



@dashboard_bp.route('/after_hours_documents', methods=['POST'])
def get_after_hours_documents():
    # Use request.json to get the JSON data sent in the POST request
    data = request.json
    db_path = data.get('db_path')

    if not db_path:
        return jsonify({"error": "Missing 'db_path' parameter"}), 400

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT file_path, owner, m_time FROM files WHERE strftime('%H:%M:%S', m_time) < '09:00:00' OR strftime('%H:%M:%S', m_time) > '18:00:00'")
    results = cursor.fetchall()

    connection.close()

    # Convert the results to the desired format
    formatted_results = [{'name': row[0], 'owner':row[1], 'time': row[2]} for row in results]

    return jsonify(formatted_results)