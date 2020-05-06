import re
from council.modules.PDFConverter import PDFConverter

class NormanConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = self.trim_text(pdf_text, "1 Roll Call", "Adjournment")
        corrected_text = self.fix_ocr(trimmed_text)
        remove_attachments = self.remove_attachments(corrected_text)
        remove_actions = self.remove_actions(remove_attachments)
        self.indent_text(remove_actions)
        return self.formatted_text

    def trim_text(self, pdf_text, start, end):
        trimmed_text = ""
        first_line = re.search(start, pdf_text)
        last_line = re.search(end, pdf_text)
        if first_line and last_line:
            trimmed_text = pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            trimmed_text = pdf_text[first_line.start():]
        elif not first_line and last_line:
            trimmed_text = pdf_text[:last_line.end()]
        elif re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n(\d{1,2}\s)?([A-Z]|\d)+-\d{4}-\d+", pdf_text):
            match = re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n(\d{1,2}\s)?([A-Z]|\d)+-\d{4}-\d+", pdf_text)
            trimmed_text = pdf_text[match.start():]
        else:
            trimmed_text = pdf_text
        return trimmed_text

    def fix_ocr(self, trimmed_text):
        fixed_text = trimmed_text.replace("\x0c", "")
        fixed_proj_codes = re.sub(r"(?P<start>\d{1,2}\s([A-Z]|\d)+)\s(?P<end>\d{4}-\d+)", r"\g<start>-\g<end>", fixed_text)
        return fixed_proj_codes
 
    def indent_text(self, trimmed_text):
        if re.match(r"\d{1,2}\s[A-Z][a-z]+|\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+", trimmed_text):
            start = re.match(r"\d{1,2}\s[A-Z][a-z]+|\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+", trimmed_text)
            end = re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+|\n[A-Z][a-z]+((\s|/)[A-Z][a-z]+)?\n", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"[A-Z][a-z]+((\s|/)[A-Z][a-z]+)?\n", trimmed_text):
            start = re.match(r"[A-Z][a-z]+((\s|/)[A-Z][a-z]+)?\n", trimmed_text)
            self.formatted_text += "<div class=\"mb-3\" style=\"text-decoration: underline\">{}</div>\n\n".format(
                trimmed_text[start.start():start.end()].strip().replace("\n", " ")
            )
            self.indent_text(trimmed_text[start.end():].strip())
        else:
            end = re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+|\n[A-Z][a-z]+((\s|/)[A-Z][a-z]+)?\n", trimmed_text)
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[:end.start()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text.strip().replace("\n", "<br>")
                )

    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 170, orig_width, orig_height - 170)
        return pdf_image.crop(crop_boundaries)

    def remove_attachments(self, text):
        slice_ranges_list = []
        attachment_text = re.finditer(r"Attachments:", text)
        for attachment in attachment_text:
            if re.search(r"ACTION NEEDED:", text[attachment.start():]):
                action_text = re.search(r"ACTION NEEDED:", text[attachment.start():])
                slice_ranges_list.append((attachment.start(), attachment.start()+action_text.start()-1))
            elif re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+|\n[A-Z][a-z]+(\s[A-Z][a-z]+)?\n", text[attachment.start():]):
                new_section = re.search(r"\n\d{1,2}\s[A-Z][a-z]+|\n\d{1,2}\s([A-Z]|\d)+-\d{4}-\d+|\n[A-Z][a-z]+(\s[A-Z][a-z]+)?\n", text[attachment.start():])
                slice_ranges_list.append((attachment.start(), attachment.start()+new_section.start()-1))
            else:
                slice_ranges_list.append((attachment.start(), len(text)))
        new_string = "".join(text[idx] for idx in range(len(text))\
            if not any(front <= idx <= rear for front, rear in slice_ranges_list))
        return new_string

    def remove_actions(self, text):
        slice_ranges_list = []
        action_text = re.finditer(r"ACTION NEEDED:", text)
        for action in action_text:
            end_of_action = re.search(r"ACTION TAKEN:\n", text[action.start():])
            slice_ranges_list.append((action.start(), action.start()+end_of_action.end()-1))
        new_string = "".join(text[idx] for idx in range(len(text))\
            if not any(front <= idx <= rear for front, rear in slice_ranges_list))
        return new_string
