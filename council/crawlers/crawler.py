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

    

    
