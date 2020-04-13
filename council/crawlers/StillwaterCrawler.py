import re
from council.modules.Crawler import Crawler

class StillwaterCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("div", id="agenda-area")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        rows = parsed_html.div.find_all("div", class_="agenda")
        for row in rows:
            if row.a:
                agenda_url = "http://stillwater.org{}".format(row.a["href"])
                agenda_date = self.create_date(row.h2.text)
                agenda_title = self.get_title(row.text)
                if not self.agenda_exists(agenda_url) and not self.too_old(agenda_date):
                    agenda = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title,
                        "agenda_url": agenda_url,
                        "agenda_text": ""
                    }
                    filtered_agendas.append(agenda)
        return filtered_agendas

    def parse_agenda(self, agenda):
        response = self.request(agenda.get("agenda_url"))
        self.set_strainer("iframe")
        soup = self.get_soup(response.text, "html.parser", parse_only=self.strainer)
        pdf_link = "http://stillwater.org{}".format(soup.iframe["src"])
        agenda.update({
            "pdf_link": pdf_link
        })
        return agenda

    @staticmethod
    def get_title(text):
        title = "Regular Meeting"
        special = re.search("\(s\)", text)
        work_session = re.search("\(w\)", text)
        if special:
            title = "Special Meeting"
        elif work_session:
            title = "Work Session"
        return title
