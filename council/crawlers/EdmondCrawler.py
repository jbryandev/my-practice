from bs4 import SoupStrainer
from council.crawlers.Crawler import Crawler
from council.crawlers.Scraper import SimpleScraper
from council.crawlers.AgendaFilter import EdmondAgendaFilter
from council.crawlers.AgendaParser import EdmondAgendaParser

class EdmondCrawler(Crawler):

    def crawl(self):
        scraper = SimpleScraper()
        agenda_filter = EdmondAgendaFilter(self.department)
        agenda_parser = EdmondAgendaParser()

        page_source = scraper.scrape(self.url, self.strainer)
        agenda_list = agenda_filter.filter(page_source)
        parsed_agendas = agenda_parser.parse(agenda_list, scraper)
        # for agenda in parsed_agendas:
            # agenda.save()

    def strainer(self):
        return SoupStrainer("tbody", class_="nowrap smallText")

    def secondary_strainer(self):
        return SoupStrainer("table", class_=" tableCollapsed")
