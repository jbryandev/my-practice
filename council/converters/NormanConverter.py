import re
from council.modules.PDFConverter import PDFConverter

class NormanConverter(PDFConverter):

    def __init__(self, agenda, progress_recorder):
        super().__init__(agenda, progress_recorder)
        self.formatted_text = ""
        self.custom_oem_psm_config = r'--oem 3 --psm 6'
        self.numbered_item_regex = r"\d{1,2}\.\sCONSIDERATION"

    def format_text(self, pdf_text):
        trimmed_text = self.trim_text(pdf_text, "Call to Order", "Adjournment")
        self.formatted_text = trimmed_text
        self.indent_text(self.formatted_text)
        return self.formatted_text

    def trim_text(self, pdf_text, start, end):
        trimmed_text = ""
        first_line = re.search(start, pdf_text, re.IGNORECASE)
        last_line = re.search(end, pdf_text, re.IGNORECASE)
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
        numbered_items = re.finditer(self.numbered_item_regex, trimmed_text)
        for item in numbered_items:
            trimmed_text = trimmed_text[:item.start()] + "<div class=\"mb-3\">" + trimmed_text[item.start():]


    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 0, orig_width, orig_height - 170)
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
        action_text = re.finditer(r"ACTION NEEDED", text)
        for action in action_text:
            end_of_action = re.search(r"ACTION TAKEN", text[action.start():])
            slice_ranges_list.append((action.start(), action.start()+end_of_action.end()))
        new_string = "".join(text[idx] for idx in range(len(text))\
            if not any(front <= idx <= rear for front, rear in slice_ranges_list))
        return new_string
