import re
from .Crawler import Crawler

class MooreCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("li", class_="public_meetings__meeting")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        for agenda in parsed_html.children:
            agenda_date = self.create_date(agenda.time.text)
            # Make sure agenda isn't older than the cutoff date
            if not self.too_old(agenda_date):
                # Check to see if agenda matches the department
                agenda_title = self.strip_title(agenda.a.text)
                if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                    # and it doesn't already exist in the database
                    agenda_url = self.get_agenda_url(agenda.a["href"])
                    if not self.agenda_exists(agenda_url) and agenda_url:
                        agenda = {
                            "agenda_date": agenda_date,
                            "agenda_title": agenda_title,
                            "agenda_url": agenda_url,
                            "pdf_link": agenda_url
                        }
                        filtered_agendas.append(agenda)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda

    def get_agenda_url(self, agenda_detail_url):
        response = self.request(agenda_detail_url)
        self.set_strainer("div", class_="accordion__item__content__wrapper")
        soup = self.get_soup(response.text, "html.parser", parse_only=self.strainer)
        if soup.a:
            agenda_url = soup.a["href"]
            return agenda_url
        return None

    @staticmethod
    def strip_title(agenda_title):
        # Remove "meeting" from end of title
        # match = re.search(r'Meeting', agenda_title)
        # if match:
        #     agenda_title = agenda_title[:match.start()-1]
        # Search for dash in title, and if found,
        # remove dash and everything before it
        match = re.search(r'-', agenda_title)
        if match:
            agenda_title = agenda_title[match.end()+1:]
        return agenda_title