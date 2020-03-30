from abc import ABC, abstractmethod

class AgendaParser(ABC):

    def __init__(self, progress_observer):
        self.progress_observer = progress_observer

    @abstractmethod
    def parse(self, agenda_list):
        pass

class EdmondAgendaParser(AgendaParser):

    def parse(self, agenda_list, scraper):
        parsed_agendas = []
        for agenda in agenda_list:
            agenda_page_source = scraper.scrape(agenda.get("agenda_url"), scraper.secondary_strainer)
            agenda_text = self.get_agenda_text(soup)
            pdf_link = self.get_pdf_link(soup)
            agenda.update({
                "agenda_text": agenda_text,
                "pdf_link": pdf_link
            })
            parsed_agendas.append(agenda)
        return parsed_agendas