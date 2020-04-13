import re
from council.modules.PDFConverter import PDFConverter

class StillwaterConverter(PDFConverter):

    @staticmethod
    def format_text(pdf_text):
        first_line = re.search("1. Call Meeting to Order", pdf_text)
        last_line = re.search("Adjourn", pdf_text)
        if first_line and last_line:
            return pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            return pdf_text[first_line.start():]
        elif not first_line and last_line:
            return pdf_text[:last_line.end()]
        else:
            return pdf_text
