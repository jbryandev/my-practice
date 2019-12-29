"""
Crawler for the City of Lawton. Lawton agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
import requests
import dateparser
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from ..modules import pdf2text

def retrieve_agendas(agendas_url):
    """
    This function takes a URL and retrieves all of the agendas
    at this location. It returns a list of agenda objects.
    """
    response = requests.get(agendas_url)
    agenda_tag = SoupStrainer("article")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_tag)
    agenda_list = []
    for agenda in soup.children:
        match = re.search("Agenda Available", agenda.text)
        if match:
            agenda_title = agenda.h3.text
            agenda_day = agenda.select(".event-card-day")[0].text
            agenda_month = agenda.select(".event-card-year")[0].text
            agenda_date = dateparser.parse(str(agenda_day + " " + agenda_month))
            agenda_detail_url = "https://www.lawtonok.gov" + agenda["about"]
            agenda_obj = {
                "agenda_date": agenda_date,
                "agenda_title": agenda_title,
                "agenda_detail_url": agenda_detail_url
            }
            agenda_list.append(agenda_obj)

    return agenda_list

def match_agendas(agenda_list, department_name):
    """
    This function takes a list of agenda dicts, as well as the department
    name to search for, and returns a list of agendas for the department.
    """
    matched_agendas = []
    for agenda in agenda_list:
        if re.search(department_name, agenda.get("agenda_title")):
            matched_agendas.append(agenda)

    return matched_agendas

def get_agenda_url(agenda_detail_url):
    """
    This function takes a URL for an agenda detail page and looks
    up the URL for the agenda document.
    """
    agenda_url = ""
    response = requests.get(agenda_detail_url)
    agenda_tag = SoupStrainer("span", class_="file-link")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_tag)
    agenda_url = soup.a["href"]

    return agenda_url

def get_agenda_text(agenda_url):
    """
    This function takes an agenda URL and returns
    the PDF content converted to text.
    """
    agenda_text = pdf2text.convert_pdf(agenda_url)

    return agenda_text
