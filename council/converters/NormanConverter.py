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
        return remove_actions
        # print(repr(remove_actions))
        # self.indent_text(remove_actions)
        # return self.formatted_text

    def fix_ocr(self, trimmed_text):
        fixed_text = trimmed_text.replace("\x0c", "")
        return fixed_text
 
    def indent_text(self, trimmed_text):
        if re.match(r"(\d{1,2}\s)*[A-Z]+[a-z]*", trimmed_text):
            start = re.match(r"(\d{1,2}\s)*[A-Z]+[a-z]*", trimmed_text)
            end = re.search(r"\n(\d{1,2}\s)*[A-Z]+[a-z]*", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        # elif re.match(r"[A-Z]{3,}", trimmed_text):
        #     start = re.match(r"[A-Z]{3,}", trimmed_text)
        #     end = re.search(r"\n(\d{1,2}|[A-Z])\)\s[A-Z][A-Za-z]{2,}|\n[A-Z]{3,}", trimmed_text[start.end():])
        #     if end:
        #         self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
        #             trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
        #         )
        #         self.indent_text(trimmed_text[end.start()+start.end():].strip())
        #     else:
        #         self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
        #             trimmed_text[start.start():].strip().replace("\n", " ")
        #         )
        # else:
        #     end = re.search(r"\n(\d{1,2}\s)*[A-Z]+[a-z]*", trimmed_text)
        #     if end:
        #         self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
        #             trimmed_text[:end.start()].strip().replace("\n", " ")
        #         )
        #         self.indent_text(trimmed_text[end.start():].strip())
        #     else:
        #         self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
        #             trimmed_text.strip().replace("\n", " ")
        #         )

    @staticmethod
    def crop_image(pdf_image):
        orig_width = pdf_image.size[0]
        orig_height = pdf_image.size[1]
        crop_boundaries = (0, 180, orig_width, orig_height - 180)
        return pdf_image.crop(crop_boundaries)

    def remove_attachments(self, text):
        replace_strings_list = []
        replace_ranges_list = []
        attachment_text = re.finditer(r"Attachments:", text)
        for attachment in attachment_text:
            action_text = re.search(r"ACTION NEEDED:", text[attachment.start():])
            replace_strings_list.append(text[attachment.start():attachment.start()+action_text.start()])
            replace_ranges_list.append({"start": attachment.start(), "end": attachment.start()+action_text.start()})
        print(replace_ranges_list)
        for text_range in replace_ranges_list:
            print(type(text_range))
            print(text_range)
            print(text_range.get("end") - text_range.get("start"))
        return re.sub("|".join(replace_strings_list), "", text)

    def remove_actions(self, text):
        replace_strings_list = []
        action_text = re.finditer(r"ACTION NEEDED:", text)
        for action in action_text:
            end_of_action = re.search(r"ACTION TAKEN:\n", text[action.start():])
            replace_strings_list.append(text[action.start():action.start()+end_of_action.end()])
        print(replace_strings_list)
        return re.sub("|".join(replace_strings_list), "", text)
