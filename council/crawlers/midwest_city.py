"""
Crawler for the City of Midwest City. MC agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
import requests
import dateutil.parser as dparser
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

def retrieve_agendas(agendas_url):
    """
    This function takes a URL and retrieves all of the agendas
    at this location. It returns a list of agenda objects.
    """
    response = requests.get(agendas_url)
    agenda_tag = SoupStrainer("table", id="table14")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_tag)
    rows = soup.find_all("tr", limit=6)
    agenda_list = []
    for agenda in rows:
        if agenda.p:
            agenda_string = agenda.p.text
            match = re.search(r'\d{4}', agenda_string)
            agenda_date = dparser.parse(agenda_string[0:match.end()], fuzzy=True)
            agenda_name = agenda_string.replace(agenda_string[0:match.end()], "").strip()
            agenda_url = "https://midwestcityok.org" + agenda.find_all("a")[2]["href"]
            agenda_obj = {
                "agenda_date": agenda_date,
                "agenda_title": agenda_name,
                "agenda_url": agenda_url
            }
            agenda_list.append(agenda_obj)

    return agenda_list

def match_agendas(agenda_list, department_name):
    """
    This function takes a list of agendas, as well as the department name
    to search for, and returns a list of agendas for the department.
    """
    matched_agendas = []
    for agenda in agenda_list:
        if re.search(department_name, agenda.get("agenda_title")):
            matched_agendas.append(agenda)

    return matched_agendas
