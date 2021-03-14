import re
from council.modules.Crawler import Crawler

class NormanCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("div", class_="views-row")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        # Limit search to 4 upcoming meetings
        meetings = parsed_html.find_all("article", limit=4)
        for agenda in meetings:
            agenda_title = agenda.a.h3.text.strip()[1:]
            # Weed out study sessions and other meetings
            if re.search("Meeting", agenda_title):
                # Check that agenda is posted
                agenda_detail_url = "http://www.normanok.gov{}".format(agenda.a["href"])
                agenda_pdf = self.get_agenda_pdf(agenda_detail_url)
                if agenda_pdf:
                    # Make sure agenda isn't already in the database
                    if not self.agenda_exists(agenda_pdf):
                        # Create date
                        agenda_date = self.create_date(agenda.a.find("p", class_="date").text.strip())
                        # Add agenda to filtered list
                        agenda_obj = {
                            "agenda_date": agenda_date,
                            "agenda_title": agenda_title,
                            "agenda_url": agenda_pdf,
                            "pdf_link": agenda_pdf
                        }
                        filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda

    def get_agenda_pdf(self, agenda_detail_url):
        response = self.request(agenda_detail_url)
        self.set_strainer("div", class_="event-description")
        soup = self.get_soup(response.text, "html.parser", parse_only=self.strainer)
        if soup.a:
            agenda_url = soup.a["href"]
            return agenda_url
        return None
