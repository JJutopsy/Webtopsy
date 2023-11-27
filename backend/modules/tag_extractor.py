import numpy as np
import pandas as pd
import sqlite3
import MeCab
from collections import Counter
import string
import networkx as nx
import time
import re

class KeywordExtractor:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.korean_pattern = re.compile('[가-힣]+')
        self.MAX_TEXT_LENGTH = 100000

    def preprocess_text(self, text):
        text = text.translate(str.maketrans("", "", string.punctuation))
        return text

    def tokenize_words(self, text):
        m = MeCab.Tagger()
        words = m.parse(text).split()
        words = [word.split('\t')[0] for word in words if 'NNG' in word and len(word) > 1]
        return words

    def create_graph(self, tokens):
        graph = nx.Graph()
        for i, token in enumerate(tokens):
            for j in range(i + 1, len(tokens)):
                if j - i > 2:
                    break
                if not graph.has_edge(token, tokens[j]):
                    graph.add_edge(token, tokens[j])
        return graph

    def textrank(self, graph, max_iter=100, tol=1e-4, damping_factor=0.85):
        pr = nx.pagerank(graph, max_iter=max_iter, tol=tol, alpha=damping_factor)
        return pr
    
    def cleanup_output(self, output):
        # Extract all Korean text using regular expression
        korean_text = re.findall(r'NNG,[^,]+,[^,]+,([^,]+),', output)
        
        # Join the extracted Korean text into a string
        cleaned_text = ', '.join(korean_text)
        return cleaned_text

    def get_top_words(self, text):
        if not text.strip() or len(text) > self.MAX_TEXT_LENGTH:
            return None

        preprocessed_text = self.preprocess_text(text)

        if self.korean_pattern.search(preprocessed_text):
            tokens = self.tokenize_words(preprocessed_text)
            word_weights = self.textrank(self.create_graph(tokens))
            top_words = [word for word, weight in sorted(word_weights.items(), key=lambda x: x[1], reverse=True)[:5]]

            # Convert the top_words list into a string using the cleanup function
            cleaned_words = self.cleanup_output(', '.join(top_words))

            return cleaned_words
        else:
            return None
    
    def extract_keywords(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT plain_text FROM files")
        texts = [text[0] for text in cursor.fetchall()]
        total_texts = len(texts)

        for i, text in enumerate(texts):
            try:
                keywords = self.get_top_words(text)
                if keywords is not None:
                    cursor.execute("UPDATE files SET tag = ? WHERE plain_text = ?", (keywords, text))

                progress_percent = (i + 1) / total_texts * 100
                print(f"Processed {i}/{total_texts} texts ({progress_percent:.2f}%)", end='\r')

            except Exception as e:
                print(f"Error processing text {i}/{total_texts}: {e}")

        self.conn.commit()
    
    def extract_keywords_eml(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT body FROM emlEmails")
        texts = [text[0] for text in cursor.fetchall()]
        total_texts = len(texts)

        for i, text in enumerate(texts):
            try:
                keywords = self.get_top_words(text)
                if keywords is not None:
                    cursor.execute("UPDATE emlEmails SET tag = ? WHERE body = ?", (keywords, text))

                progress_percent = (i + 1) / total_texts * 100
                print(f"Processed {i}/{total_texts} texts ({progress_percent:.2f}%)", end='\r')

            except Exception as e:
                print(f"Error processing text {i}/{total_texts}: {e}")

        self.conn.commit()
        
    def extract_keywords_emlAttachments(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT plain_text FROM emlAttachments")
        texts = [text[0] for text in cursor.fetchall()]
        total_texts = len(texts)

        for i, text in enumerate(texts):
            try:
                keywords = self.get_top_words(text)
                if keywords is not None:
                    cursor.execute("UPDATE emlAttachments SET tag = ? WHERE plain_text = ?", (keywords, text))

                progress_percent = (i + 1) / total_texts * 100
                print(f"Processed {i}/{total_texts} texts ({progress_percent:.2f}%)", end='\r')

            except Exception as e:
                print(f"Error processing text {i}/{total_texts}: {e}")

        self.conn.commit()
        
    def extract_keywords_pstAttachments(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT plain_text FROM pstAttachments")
        texts = [text[0] for text in cursor.fetchall()]
        total_texts = len(texts)

        for i, text in enumerate(texts):
            try:
                keywords = self.get_top_words(text)
                if keywords is not None:
                    cursor.execute("UPDATE pstAttachments SET tag = ? WHERE plain_text = ?", (keywords, text))

                progress_percent = (i + 1) / total_texts * 100
                print(f"Processed {i}/{total_texts} texts ({progress_percent:.2f}%)", end='\r')

            except Exception as e:
                print(f"Error processing text {i}/{total_texts}: {e}")

        self.conn.commit()