from abc import ABC, abstractmethod
from datetime import datetime
from django.utils import timezone
import dateutil.parser as dparser
import requests
from bs4 import BeautifulSoup, SoupStrainer
from council.models import Agenda
from council.crawlers.ProgressObserver import ProgressObserver
from council.modules import chromedriver

class Crawler(ABC):

    def __init__(self, department, progress_recorder):
        self.name = department.department_name
        self.url = department.agendas_url
        self.department = department
        self.max_days_old = 30
        self.progress_observer = ProgressObserver(progress_recorder)
        self.strainer = SoupStrainer()

    def __repr__(self):
        return self.name

    def crawl(self):
        # Connect to City website and get page source
        status = "Connecting to City website..."
        self.progress_observer.update(0, 10, status, 1)
        page_source = self.get_page_source(self.url)

        # Parse the extracted page source
        status = "Connection succeeded. Getting page data..."
        self.progress_observer.update(1, 10, status)
        parsed_html = self.parse_html(page_source)

        # Filter agendas that match desired criteria
        status = "Searching for new {} agendas...".format(self.name)
        self.progress_observer.update(2, 10, status)
        filtered_agendas = self.filter_agendas(parsed_html)
        status = "Found {} new agenda(s).".format(len(filtered_agendas))
        self.progress_observer.update(3, 10, status)

        # Loop over filtered agendas, parse out the info, and save to database
        i = 1
        progress_step = 3
        progress_length = len(filtered_agendas)*2 + 4
        for agenda in filtered_agendas:
            # Parse out agenda information
            status = "Getting contents of agenda {} of {}...".format(i, len(filtered_agendas))
            progress_step += 1
            self.progress_observer.update(progress_step, progress_length, status)
            parsed_agenda = self.parse_agenda(agenda)

            # Save agenda to database
            status = "Saving agenda {} of {} to the database...".format(i, len(filtered_agendas))
            progress_step += 1
            self.progress_observer.update(progress_step, progress_length, status)
            new_agenda = self.create_new_agenda(parsed_agenda)
            new_agenda.save()
            i += 1

    def get_page_source(self, url):
        return self.request(url).text

    def parse_html(self, page_source):
        return self.get_soup(page_source, "html.parser", parse_only=self.strainer)

    @abstractmethod
    def filter_agendas(self, parsed_html):
        """ Returns a filtered list of agendas matching given criteria. """

    @abstractmethod
    def parse_agenda(self, agenda):
        """ Returns a parsed agenda. """


    def set_strainer(self, tag, **kwargs):
        self.strainer = SoupStrainer(tag, **kwargs)

    @staticmethod
    def request(url, timeout=10):
        return requests.get(url, timeout=timeout)

    @staticmethod
    def get_browser(url):
        return chromedriver.open_browser(url)

    @staticmethod
    def get_soup(page_source, parser, **kwargs):
        return BeautifulSoup(page_source, parser, **kwargs)

    @staticmethod
    def agenda_exists(agenda_url):
        return bool(Agenda.objects.filter(agenda_url=agenda_url).exists())

    @staticmethod
    def get_current_date():
        return datetime.now(tz=timezone.get_current_timezone())

    @staticmethod
    def create_date(date_string):
        return timezone.make_aware(dparser.parse(date_string, fuzzy=True))

    def too_old(self, date):
        return bool((self.get_current_date() - date).days > self.max_days_old)

    def create_new_agenda(self, agenda_info):
        agenda = Agenda(
            agenda_date=agenda_info.get("agenda_date"),
            agenda_title=agenda_info.get("agenda_title"),
            agenda_url=agenda_info.get("agenda_url"),
            agenda_text=agenda_info.get("agenda_text"),
            pdf_link=agenda_info.get("pdf_link"),
            date_added=self.get_current_date(),
            department=self.department
        )
        return agenda
