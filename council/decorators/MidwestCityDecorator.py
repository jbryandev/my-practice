import re
from django.utils.html import linebreaks
from council.modules.PDFConverterDecorator import PDFConverterDecorator

class MidwestCityDecorator(PDFConverterDecorator):

    def format_text(self):
        match = re.search("CALL TO ORDER", self.pdf_text)
        if match:
            return linebreaks(self.pdf_text[match.start():])
        else:
            return linebreaks(self.pdf_text)
