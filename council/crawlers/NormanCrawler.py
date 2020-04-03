import re
from .Crawler import Crawler

class NormanCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table", id="filebrowser-file-listing")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        # Limit search to 5 most-recent agendas
        rows = parsed_html.tbody.find_all("tr", limit=5)
        for agenda in rows:
            # The first row is not an agenda, which can be confirmed by the absence
            # of filesize text. Agenda.contents[2] is where the filesize is found.
            if agenda.contents[2].text:
                agenda_url = "http://www.normanok.gov{}".format(agenda.a["href"])
                # Make sure agenda isn't already in the database
                if not self.agenda_exists(agenda_url):
                    # Separate out date and title
                    match = re.search(r'\d{1,4}-\d{1,2}-\d{1,2}', agenda.a.text)
                    agenda_date = self.create_date(match.group(0))
                    agenda_title = agenda.a.text[match.end():len(agenda.a.text)].strip()
                    # Check to see if agenda title matches the department
                    if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                        # Make sure agenda isn't older than the cutoff date
                        if not self.too_old(agenda_date):
                            agenda_obj = {
                                "agenda_date": agenda_date,
                                "agenda_title": agenda_title,
                                "agenda_url": agenda_url,
                                "pdf_link": agenda_url
                            }
                            filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda
