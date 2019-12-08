"""
Crawler for the City of Moore. Moore agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from council.modules import pdf2text

def retrieve_agendas(agendas_url):
    """
    This function takes a URL and retrieves all of the agendas
    at this location. It returns a list of agenda objects.
    """
    response = requests.get(agendas_url)
    agenda_li = SoupStrainer("li", class_="public_meetings__meeting")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_li)
    agenda_list = []
    for agenda in soup.children:
        agenda_date = agenda.time.text
        agenda_title = agenda.a.text
        agenda_detail = agenda.a["href"]
        agenda_obj = {
            "agenda_date": agenda_date,
            "agenda_title": agenda_title,
            "agenda_detail": agenda_detail
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
    to see if an actual agenda has been posted. If so, it returns
    the URL to the agenda. If not, it returns False.
    """
    agenda_url = ""
    response = requests.get(agenda_detail_url)
    agenda_div = SoupStrainer("div", class_="accordion__item__content__wrapper")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_div)
    if soup.a:
        agenda_url = soup.a["href"]
        return agenda_url
    else:
        return False

def get_agenda_text(agenda_url):
    """
    This function takes an agenda URL and returns
    the PDF content converted to text.
    """
    agenda_text = pdf2text(agenda_url)

    return agenda_text
