from abc import ABC, abstractmethod
from datetime import datetime
from django.utils import timezone
import dateutil.parser as dparser
from council.models import Agenda

class AgendaFilter(ABC):

    def __init__(self, department):
        self.department = department

    @abstractmethod
    def filter(self, page_source):
        pass

    @staticmethod
    def create_date(date_string):
        return timezone.make_aware(dparser.parse(date_string, fuzzy=True))

    @staticmethod
    def agenda_exists(agenda_url):
        return bool(Agenda.objects.filter(agenda_url=agenda_url).exists())

class EdmondAgendaFilter(AgendaFilter):

    def filter(self, page_source):
        agenda_list = []
        rows = page_source.find_all("tr")
        for row in rows:
            agenda_url = "http://agenda.edmondok.com:8085/{}".format(row.a["href"])
            agenda_date = self.create_date(row.a.text)
            agenda_title = row.find_all("td")[1].text
            # Check to see if agenda matches the department
            if agenda_title.lower().strip() == self.department.department_name.lower().strip():
                # and doesn't already exist in the database
                if not self.agenda_exists(agenda_url):
                    agenda = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title,
                        "agenda_url": agenda_url,
                    }
                    agenda_list.append(agenda)
        return agenda_list