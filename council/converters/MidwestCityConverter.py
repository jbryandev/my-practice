import re, unicodedata
from council.modules.PDFConverter import PDFConverter

class MidwestCityConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = self.trim_text(pdf_text, "CALL TO ORDER", "ADJOURNMENT")
        print(repr(trimmed_text))
        corrected_text = self.fix_ocr(trimmed_text)
        self.indent_text(corrected_text)
        return self.formatted_text

    def fix_ocr(self, trimmed_text):
        fixed_text = trimmed_text.replace("\x0c", "")
        match = re.search(r"\n\d{1,2}\,\s[A-Z]", fixed_text)
        if match:
            return fixed_text.replace(match.group(0), match.group(0).replace(",", "."))
        else:
            return fixed_text

    def indent_text(self, trimmed_text):
        if re.match(r"[A-Z]{3,}", trimmed_text):
            start = re.match(r"[A-Z]{3,}", trimmed_text)
            end = re.search(r"\n[A-Z]{3,}|\n\d{1,2}\.\s[A-Z]|\n\n[A-Z|\d{1,2}]", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text):
            start = re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text)
            end = re.search(r"\n[A-Z]{3,}|\n\d{1,2}\.\s[A-Z]|\n\n[A-Z|\d{1,2}]", trimmed_text[start.end():])
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
            end = re.search(r"\n[A-Z]{3,}|\n\d{1,2}\.\s[A-Z]|\n\n[A-Z|\d{1,2}]", trimmed_text)
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[:end.start()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text.strip().replace("\n", " ")
                )

    
