import re
from council.crawlers.TulsaCrawler import TulsaCrawler

class TulsaCouncilCrawler(TulsaCrawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table")
        self.formatted_text = ""

    def format_text(self, text):
        # Determine format of agenda
        # Regular council meetings use different format
        # Than workshop council meetings
        if re.search("01. Call to Order", text):
            self.format_workshop(text)
        else:
            self.format_regular_meeting(text)
        return self.formatted_text

    def format_workshop(self, text):
        # Format council workshop agenda
        pass

    def format_regular_meeting(self, text):
        # Format regular council meeting agenda
        trimmed_text = self.trim_text(text, r"1.\s+RECEIPT", "Adjournment")
        self.indent_regular_text(trimmed_text)

    def indent_regular_text(self, trimmed_text):
        if re.match(r"\d{1,2}.\s+[A-Z]{2,}", trimmed_text):
            start = re.match(r"\d{1,2}.\s+[A-Z]{2,}", trimmed_text)
            end = re.search(r"\n[a-z]\.\n([A-Z][a-z]+|[A-Z]{2,})", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ")
                )
                self.indent_regular_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"[a-z]\.\n([A-Z][a-z]+|[A-Z]{2,})", trimmed_text):
            start = re.match(r"[a-z]\.\n([A-Z][a-z]+|[A-Z]{2,})", trimmed_text)
            end = re.search(r"\n[a-z]\.\n([A-Z][a-z]+|[A-Z]{2,})|\n\(\d{1,2}\)\s[A-Z][a-z]+|\n\d{1,2}.\s+[A-Z]{2,}", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ").replace("BackupDocumentation", "")
                )
                self.indent_regular_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
        elif re.match(r"\(\d{1,2}\)\s[A-Z][a-z]+", trimmed_text):
            start = re.match(r"\(\d{1,2}\)\s[A-Z][a-z]+", trimmed_text)
            end = re.search(r"\n[a-z]\.\n([A-Z][a-z]+|[A-Z]{2,})|\n\(\d{1,2}\)\s[A-Z][a-z]+|\n\d{1,2}.\s+[A-Z]{2,}", trimmed_text[start.end():])
            if end:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.5in\">{}</div>\n\n".format(
                    trimmed_text[start.start():end.start()+start.end()].strip().replace("\n", " ").replace("BackupDocumentation", "")
                )
                self.indent_regular_text(trimmed_text[end.start()+start.end():].strip())
            else:
                self.formatted_text += "<div class=\"mb-3\" style=\"padding-left: 0.5in\">{}</div>\n\n".format(
                    trimmed_text[start.start():].strip().replace("\n", " ")
                )
