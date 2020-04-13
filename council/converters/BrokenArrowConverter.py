import re
from council.modules.PDFConverter import PDFConverter

class BrokenArrowConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = ""
        first_line = re.search("1. Call to Order", pdf_text)
        last_line = re.search("Adjournment", pdf_text)
        if first_line and last_line:
            trimmed_text = pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            trimmed_text = pdf_text[first_line.start():]
        elif not first_line and last_line:
            trimmed_text = pdf_text[:last_line.end()]
        else:
            trimmed_text = pdf_text
        # return trimmed_text
        self.indent_text(trimmed_text)
        return self.formatted_text

    def indent_text(self, trimmed_text):
        if re.match(r"\d{1,2}\.[^\S][A-Z]", trimmed_text):
            start = re.match(r"\d{1,2}\.[^\S][A-Z]", trimmed_text)
            end = re.search(r"\n[A-Z0-9]{1,2}\.[^\S]", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.end()]
                )
                self.indent_text(trimmed_text[end.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():]
                )
        elif re.match(r"[A-Z0-9]{1,2}\.[^\S]\d", trimmed_text):
            start = re.match(r"[A-Z0-9]{1,2}\.[^\S]\d", trimmed_text)
            end = re.search(r"\n[A-Z0-9]{1,2}\.[^\S]", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.end()]
                )
                self.indent_text(trimmed_text[end.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():]
                )

    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 0, orig_width, orig_height - 150)
        return pdf_image.crop(crop_boundaries)
