from tika import parser
import tempfile
import os

class OLEExtractor:
    def __init__(self, file_data):
        self._file_data = file_data
        self.text = self._get_text()

    def _get_text(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(self._file_data)
            temp_file_path = temp_file.name

        try:
            parsed = parser.from_file(temp_file_path)
            return parsed['content'].strip() if parsed.get('content') else ""
        finally:
            os.remove(temp_file_path)  # 임시 파일을 삭제

    def get_text(self):
        return self.text