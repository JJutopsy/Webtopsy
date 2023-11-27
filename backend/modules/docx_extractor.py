import io
import xml.etree.ElementTree as ET
import zipfile

class DOCXExtractor:
    NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = NAMESPACE + 'p'
    TEXT = NAMESPACE + 't'

    def __init__(self, file_data):  # filename 대신 file_data를 파라미터로 받음
        self._file_data = file_data  # _filename 대신 _file_data를 사용
        self.text = self._get_text()

    def _get_text(self):
        # io.BytesIO를 사용하여 바이트 데이터를 파일처럼 사용
        with zipfile.ZipFile(io.BytesIO(self._file_data)) as document:  
            xml_content = document.read('word/document.xml').decode()
            # document.close()는 with 문에서 자동으로 처리되므로 삭제
            tree = ET.fromstring(xml_content)

        paragraphs = [
            ''.join([node.text for node in paragraph.findall('.//' + self.TEXT) if node.text])
            for paragraph in tree.findall('.//' + self.PARA)
        ]

        return '\n\n'.join(paragraphs)

    def get_text(self):
        return self.text
