import xml.etree.ElementTree as ET
import zipfile
import io  # io 모듈을 추가

class PPTXExtractor:
    NAMESPACE = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
    TEXT = NAMESPACE + 't'
    SLIDE_PREFIX = "ppt/slides/slide"
    SLIDE_PREFIX_LENGTH = len(SLIDE_PREFIX)

    def __init__(self, file_data):  # filename을 file_data로 변경
        self._file_data = file_data  # filename을 file_data로 변경
        self.text = self._get_text()

    def _get_text(self):
        # filename을 file_data로 변경하고, zipfile.ZipFile의 인수를 io.BytesIO(file_data)로 변경
        document = zipfile.ZipFile(io.BytesIO(self._file_data))
        slides = self._get_slide_names(document.namelist())
        texts = [self._extract_text_from_slide(document, slide) for slide in slides]
        document.close()
        return '\n'.join(texts)

    def _get_slide_names(self, dirs):
        return sorted(
            [d for d in dirs if d.startswith(self.SLIDE_PREFIX) and d.endswith('.xml')]
        )

    def _extract_text_from_slide(self, document, slide):
        xml_content = document.read(slide).decode()
        tree = ET.fromstring(xml_content)
        texts = [node.text for node in tree.findall('.//' + self.TEXT) if node.text]
        return '\n'.join(texts)

    def get_text(self):
        return self.text