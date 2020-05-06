import re
from council.modules.PDFConverter import PDFConverter

class MooreConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = self.trim_text(pdf_text, "1\) CALL TO ORDER", "ADJOURNMENT")
        corrected_text = self.fix_ocr(trimmed_text)
        remove_page = re.sub(r"Page\s*\d{1,3}", "", corrected_text)
        remove_action = re.sub(r"ACTION:", "", remove_page)
        remove_dbl_space = re.sub(r"([A-Z])\n+([A-Z])", r"\1 \2", remove_action)
        self.indent_text(remove_dbl_space)
        return self.formatted_text

    def fix_ocr(self, trimmed_text):
        fixed_text = trimmed_text.replace("\x0c", "")
        return fixed_text
 
    def indent_text(self, trimmed_text):
        if re.match(r"\d{1,2}\)\s[A-Z][A-Za-z]{2,}", trimmed_text):
            start = re.match(r"\d{1,2}\)\s[A-Z][A-Za-z]{2,}", trimmed_text)
            end = re.search(r"\n(\d{1,2}|[A-Z])\)\s[A-Z][A-Za-z]{2,}|\n[A-Z]{3,}", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"[A-Z]{3,}", trimmed_text):
            start = re.match(r"[A-Z]{3,}", trimmed_text)
            end = re.search(r"\n(\d{1,2}|[A-Z])\)\s[A-Z][A-Za-z]{2,}|\n[A-Z]{3,}", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        else:
            end = re.search(r"\n(\d{1,2}|[A-Z])\)\s[A-Z][A-Za-z]{2,}|\n[A-Z]{3,}", trimmed_text)
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[:end.start()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text.strip().replace("\n", " ")
                )
