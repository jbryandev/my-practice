from abc import abstractmethod
from .PDFConverter import PDFConverter

class PDFConverterDecorator(PDFConverter):

    @abstractmethod
    def format_text(self):
        pass
