import re
from council.modules.Crawler import Crawler

class MidwestCityCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table", id="table14")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        rows = parsed_html.find_all("tr", limit=5)
        for agenda in rows:
            if agenda.p:
                agenda_string = agenda.p.text
                match = re.search(r'\d{4}', agenda_string)
                agenda_date = self.create_date(agenda_string[0:match.end()])
                # Make sure agenda isn't older than the cutoff date
                if not self.too_old(agenda_date):
                    agenda_title = agenda_string.replace(agenda_string[0:match.end()], "").strip()
                    # Check to see if agenda matches the department
                    if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                        agenda_url = "https://midwestcityok.org{}".format(agenda.find_all("a")[2]["href"])
                        # and doesn't already exist in the database
                        if not self.agenda_exists(agenda_url):
                            agenda = {
                                "agenda_date": agenda_date,
                                "agenda_title": agenda_title,
                                "agenda_url": agenda_url,
                                "agenda_text": "", # will be generated upon user request
                                "pdf_link": agenda_url
                            }
                            filtered_agendas.append(agenda)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda
