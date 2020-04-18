import re

class TestConverter:

    def __init__(self):
        self.formatted_text = ""

    def format_text(self, pdf_text):
        trimmed_text = ""
        first_line = re.search("1. Call Meeting to Order", pdf_text)
        last_line = re.search("Adjourn", pdf_text)
        if first_line and last_line:
            trimmed_text = pdf_text[first_line.start():last_line.end()]
        elif first_line and not last_line:
            trimmed_text = pdf_text[first_line.start():]
        elif not first_line and last_line:
            trimmed_text = pdf_text[:last_line.end()]
        else:
            trimmed_text = pdf_text
        return trimmed_text.replace("|", "")

    def fix_ocr(self, text):
        new_text = ""
        proj_refs = re.finditer(r"[A-Z]{2}-\d{2}-\d{2}\s*[A-Za-z]*\s[A-Za-z]*\n", text)
        i = 1
        for match in proj_refs:
            print("Run " + str(i))
            print(match)
            end_line = re.search("\n\n", text[match.end():])
            new_text += text[match.end():match.end() + end_line.start()] + " ({})".format(text[match.start():match.end()].strip())
            i += 1
        print(new_text)
        return new_text.replace("|", "")

    def indent_text(self, trimmed_text):
        if re.match(r"\d{1,2}\.\s*[A-Z]", trimmed_text):
            start = re.match(r"\d{1,2}\.\s*[A-Z]", trimmed_text)
            end = re.search(r"(\s[a-z0-9]{1,2}\.\s*[A-Z])|(\s[A-Z]{2}\s[A-Z])", trimmed_text[start.end():])
            if end:
                print("----------block----------")
                print(trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " "))
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"([a-z]{1,2}\.\s*[A-Z])|([A-Z]{2}\s[A-Z])", trimmed_text):
            start = re.match(r"([a-z]{1,2}\.\s*[A-Z])|([A-Z]{2}\s[A-Z])", trimmed_text)
            end = re.search(r"(\s[a-z0-9]{1,2}\.\s*[A-Z])|([A-Z]{2}\s[A-Z])", trimmed_text[start.end():])
            if end:
                print("----------block----------")
                print(trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " "))
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_text(trimmed_text[end.start()+start.end():].strip())
            else:
                print(trimmed_text[start.start():].strip().replace("\n", " "))
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
