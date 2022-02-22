import re
from datetime import date
from council.modules.PDFConverter import PDFConverter

class BrokenArrowConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""
        self.first_level_regex = r"\d{1,2}\.\s"
        self.second_level_regex = r"[A-Za-z]{1,2}\.*\s\d{2}-\d|2\d-\d{1,4}\s"
        self.full_regex = r"\d{1,2}\.\s|[A-Za-z]{1,2}\.*\s\d{2}-\d|2\d-\d{1,4}\s"

    def format_text(self, pdf_text):
        trimmed_text = ""
        first_line = re.search(self.first_level_regex, pdf_text)
        last_line = re.search("Adjournment", pdf_text)
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
        match = re.search(r"[A-Z]{1,2}\,\s\d{1,2}-", trimmed_text)
        if match:
            return trimmed_text.replace(match.group(0), match.group(0).replace(",", "."))
        else:
            return trimmed_text

    def indent_text(self, trimmed_text):
        # Looks for numbered lines and indents them (first-level indent)
        if re.match(self.first_level_regex, trimmed_text):
            start = re.match(self.first_level_regex, trimmed_text)
            end = re.search(self.full_regex, trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        # Looks for lettered lines and indents them (second-level indent)
        elif re.match(self.second_level_regex, trimmed_text):
            start = re.match(self.second_level_regex, trimmed_text)
            end = re.search(self.full_regex, trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        # Failback if no lines are found for indentation
        # (ie the regexes above don't match anything)
        # (usually means tesseract output is bad)
        else:
            self.formatted_text = trimmed_text

    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 0, orig_width, orig_height - 150)
        return pdf_image.crop(crop_boundaries)
