import re
from council.crawlers.Crawler import Crawler

class LawtonCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("article")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        for agenda in parsed_html.children:
            agenda_title = agenda.h3.text.strip()
            # If agenda title matches the current department...
            if agenda_title.lower() == self.name.lower():
                # And if the agenda is available...
                match = re.search("Agenda Available", agenda.text)
                if match:
                    # Store agenda information and append to agenda list
                    agenda_day = agenda.select(".event-card-day")[0].text
                    agenda_month = agenda.select(".event-card-year")[0].text
                    agenda_date = self.create_date("{} {}".format(agenda_day, agenda_month))
                    agenda_url = "https://www.lawtonok.gov{}".format(agenda["about"])
                    agenda_obj = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title,
                        "agenda_url": agenda_url
                    }
                    filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        response = self.request(agenda.get("agenda_url"))
        self.set_strainer("span", class_="file-link")
        soup = self.get_soup(response, "html.parser", parse_only=self.strainer)
        pdf_link = soup.a["href"]
        agenda.update({"pdf_link": pdf_link})
        return agenda
