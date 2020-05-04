import re
from council.modules.PDFConverter import PDFConverter

class ElRenoConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = ""
        first_line = re.search(r"A\s*CALL MEETING TO ORDER", pdf_text)
        last_line = re.search("ADJOURNMENT", pdf_text)
        if first_line and last_line:
            trimmed_text = pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            trimmed_text = pdf_text[first_line.start():]
        elif not first_line and last_line:
            trimmed_text = pdf_text[:last_line.end()]
        else:
            trimmed_text = pdf_text
        corrected_text = self.fix_ocr(trimmed_text)
        self.indent_text(corrected_text)
        return self.formatted_text

    def fix_ocr(self, trimmed_text):
        fixed_text = trimmed_text.replace("\x0c", "\n")
        match = re.search(r"\n1\s", fixed_text)
        if match:
            return fixed_text.replace(match.group(0), match.group(0).replace("\n1 ", "\nI "))
        else:
            return fixed_text

    def indent_text(self, trimmed_text):
        if re.match(r"[A-Z]\s[A-Z]", trimmed_text):
            start = re.match(r"[A-Z]\s[A-Z]", trimmed_text)
            end = re.search(r"\d{1,2}\.\s[A-Z]|\n\n|\n[A-Z]\s[A-Z]", trimmed_text[start.end():])
            if end:
                pre_text = trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                post_text = pre_text[:1] + ". " + pre_text[2:]
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(post_text)
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                pre_text = trimmed_text[start.start():].strip().replace("\n", " ")
                post_text = pre_text[:1] + ". " + pre_text[2:]
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(post_text)
        elif re.match(r"[a-z]\s[A-Z]", trimmed_text):
            start = re.match(r"[a-z]\s[A-Z]", trimmed_text)
            end = re.search(r"\d{1,2}\.\s[A-Z]|\n\n|\n[A-Z]\s[A-Z]", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text):
            start = re.match(r"\d{1,2}\.\s[A-Z]", trimmed_text)
            end = re.search(r"\d{1,2}\.\s[A-Z]|\n\n|\n[A-Z]\s[A-Z]", trimmed_text[start.end():])
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
            end = re.search(r"\d{1,2}\.\s[A-Z]|\n\n|\n[A-Z]\s[A-Z]", trimmed_text)
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[:end.start()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text.strip().replace("\n", " ")
                )

    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 200, orig_width, orig_height)
        return pdf_image.crop(crop_boundaries)
