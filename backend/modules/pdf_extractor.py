import fitz  # PyMuPDF 라이브러리
import io
import logging

class PDFExtractor:
    def __init__(self, file_data):
        self.file_data = file_data

    def get_text(self):
        text = ""
        pdf_stream = io.BytesIO(self.file_data)
        try:
            with fitz.open(stream=pdf_stream, filetype="pdf") as pdf:
                for page in pdf:
                    text += page.get_text()
        except Exception as e:
            logging.error(f"PDF text extraction error: {e}")
            text = ""
        return text.strip()