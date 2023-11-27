import olefile
import zlib
import struct
import re
import io  # io 모듈 추가

# HWPExtractor 클래스
class HWPExtractor:
    FILE_HEADER_SECTION = "FileHeader"
    HWP_SUMMARY_SECTION = "\x05HwpSummaryInformation"
    SECTION_NAME_LENGTH = len("Section")
    BODYTEXT_SECTION = "BodyText"
    HWP_TEXT_TAGS = [67]

    def __init__(self, file_data):
        self._ole = self.load(file_data)
        self._dirs = self._ole.listdir()

        self._valid = self.is_valid(self._dirs)
        if not self._valid:
            raise Exception("Not a valid HwpFile")
        
        self._compressed = self.is_compressed(self._ole)
        self.text = self._get_text()

    def load(self, file_data):
        return olefile.OleFileIO(io.BytesIO(file_data))  # io.BytesIO를 사용하여 바이트 데이터를 파일처럼 처리

    def is_valid(self, dirs):
        if [self.FILE_HEADER_SECTION] not in dirs:
            return False

        return [self.HWP_SUMMARY_SECTION] in dirs

    def is_compressed(self, ole):
        header = self._ole.openstream("FileHeader")
        header_data = header.read()
        return (header_data[36] & 1) == 1

    def get_body_sections(self, dirs):
        m = []
        for d in dirs:
            if d[0] == self.BODYTEXT_SECTION:
                m.append(int(d[1][self.SECTION_NAME_LENGTH:]))

        return ["BodyText/Section"+str(x) for x in sorted(m)]

    def get_text(self):
        return self.text

    def _get_text(self):
        sections = self.get_body_sections(self._dirs)
        text = ""
        for section in sections:
            text += self.get_text_from_section(section)
            text += "\n"

        # 텍스트에서 한글, 영어, 숫자를 제외한 모든 문자 제거
        text = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", text)

        self.text = text
        return self.text

    def get_text_from_section(self, section):
        bodytext = self._ole.openstream(section)
        data = bodytext.read()

        unpacked_data = zlib.decompress(data, -15) if self.is_compressed else data
        size = len(unpacked_data)

        i = 0

        text = ""
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            level = (header >> 10) & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in self.HWP_TEXT_TAGS:
                rec_data = unpacked_data[i+4:i+4+rec_len]
                text += rec_data.decode('utf-16')
                text += "\n"

            i += 4 + rec_len

        return text
        

def get_text(filename):
    hwp = HWPExtractor(filename) 
    print(hwp.get_text())