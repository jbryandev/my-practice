import re, unicodedata
from council.modules.Crawler import Crawler

class BrokenArrowCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table", class_="rgMasterTable")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        rows = parsed_html.tbody.find_all("tr")
        for agenda in rows:
            agenda_dept = unicodedata.normalize("NFKD", agenda.td.text.strip())
            agenda_status = unicodedata.normalize("NFKD", agenda.find_all("td")[6].text.strip())
            agenda_type = unicodedata.normalize("NFKD", agenda.find_all("td")[4].text.strip())
            agenda_date_string = agenda.find_all("td")[1].text.strip()
            # Check for department match
            if re.search(self.department.department_name.lower(), agenda_dept.lower()):
                # Make sure agenda is available and not a cancelled meeting
                if not agenda_status.lower() == "not available":
                    if not re.search("cancelled", agenda_status.lower()):
                        # Verify agenda date is not too old
                        agenda_date = self.create_date(agenda_date_string)
                        if not self.too_old(agenda_date):
                            # Verify agenda not already in database
                            agenda_url = "https://brokenarrow.legistar.com/{}".format(
                                agenda.find_all("td")[6].a["href"]
                            )
                            if not self.agenda_exists(agenda_url):
                                agenda_obj = {
                                    "agenda_date": agenda_date,
                                    "agenda_title": self.get_title(agenda_type),
                                    "agenda_url": agenda_url,
                                    "agenda_text": "", # will be generated upon user request
                                    "pdf_link": agenda_url
                                }
                                filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda

    @staticmethod
    def get_title(text):
        title = "Regular Meeting"
        special = re.search("special", text.lower())
        if special:
            title = "Special Meeting"
        return title
