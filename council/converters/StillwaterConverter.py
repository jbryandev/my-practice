import re
from bs4 import BeautifulSoup
from council.modules.PDFConverter import PDFConverter
from council.modules.OCRProcessor import OCRProcessor

class StillwaterConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""
        self.ocr_config = r'--oem 3 --psm 4'

    def extract_text(self, pdf_image):
        ocr = OCRProcessor()
        return ocr.process(pdf_image, config=self.ocr_config)
        # hocr = ocr.process(pdf_image, config=self.ocr_config, mode='hocr')
        # soup = BeautifulSoup(hocr, "html.parser")
        # lines = soup.find_all("span", class_="ocr_line")
        # pdf_text = ""
        # for line in lines:
        #     pdf_text += line.text.strip().replace("|", "").replace("\n", " ")
        # return pdf_text
    
    def format_text(self, extracted_text):
        clean_text = extracted_text.replace("\x0c", "\n").replace("|", "")
        trimmed_text = self.trim_text(clean_text)
        self.formatted_text = ""
        self.indent_text(trimmed_text)
        return self.formatted_text
        # return trimmed_text

    def trim_text(self, pdf_text):
        first_line = re.search("1. Call Meeting to Order", pdf_text)
        last_line = re.search("Adjourn", pdf_text)
        if first_line and last_line:
            trimmed_text = pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            trimmed_text = pdf_text[first_line.start():]
        elif not first_line and last_line:
            trimmed_text = pdf_text[:last_line.end()]
        else:
            trimmed_text = pdf_text
        return trimmed_text

    def indent_text(self, trimmed_text):
        if re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text):
            start = re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text)
            end = re.search(r"\n", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip()
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip()
                )
        elif re.match(r"[a-z]{1,2}\.\s", trimmed_text):
            start = re.match(r"[a-z]{1,2}\.\s", trimmed_text)
            end = re.search(r"\n[a-z]\.\s|\n\n", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        else:
            end = re.search(r"\n\n", trimmed_text)
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[:end.start()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text.strip().replace("\n", " ")
                )
