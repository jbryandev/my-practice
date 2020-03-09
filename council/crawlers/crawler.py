from datetime import datetime
from django.utils import timezone
import dateutil.parser as dparser
import requests
from bs4 import BeautifulSoup, SoupStrainer
from council.models import Agenda

class Crawler:

    def __init__(self, department):
        self.name = department.department_name
        self.url = department.agendas_url
        self.department = department
        self.max_days_old = 30

    def __repr__(self):
        return self.name

    def get_url(self, url, timeout=10):
        return requests.get(url, timeout=timeout)

    def get_strainer(self, tag, **kwargs):
        return SoupStrainer(tag, **kwargs)

    def get_soup(self, response, parser, **kwargs):
        return BeautifulSoup(response.text, parser, **kwargs)

    def agenda_exists(self, agenda_url):
        return bool(Agenda.objects.filter(agenda_url=agenda_url).exists())

    def get_current_date(self):
        return datetime.now(tz=timezone.get_current_timezone())

    def create_date(self, date_string):
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
