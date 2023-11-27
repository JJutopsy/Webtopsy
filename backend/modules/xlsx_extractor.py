import xml.etree.ElementTree as ET
import zipfile
import io  # io 모듈을 추가

# XLSXExtractor 클래스
class XLSXExtractor:
    NAMESPACE = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    TEXT = NAMESPACE + 't'
    SHARED_STRINGS = 'xl/sharedStrings.xml'

    def __init__(self, file_data):  # filename을 file_data로 변경
        self._file_data = file_data  # filename을 file_data로 변경
        self.text = self._get_text()

    def _get_text(self):
        # filename을 file_data로 변경하고, zipfile.ZipFile의 인수를 io.BytesIO(file_data)로 변경
        document = zipfile.ZipFile(io.BytesIO(self._file_data))
        xml_content = document.read(self.SHARED_STRINGS).decode()
        document.close()
        tree = ET.fromstring(xml_content)
        texts = [node.text for node in tree.findall('.//' + self.TEXT) if node.text]
        return '\n'.join(texts)

    def get_text(self):
        return self.text