"""
Crawler for the City of Norman. Norman agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
import requests
import dateutil.parser as dparser
from bs4 import BeautifulSoup, SoupStrainer
from ..modules import pdf2text

def retrieve_agendas(agendas_url):
    """
    This function takes a URL and retrieves all of the agendas
    at this location. It returns a list of agenda objects.
    """
    response = requests.get(agendas_url)
    agenda_table = SoupStrainer("table", id="filebrowser-file-listing")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_table)
    # Limit search to 5 most-recent agendas
    agendas = soup.tbody.find_all("tr", limit=5)
    agenda_list = []
    for agenda in agendas:
        # The first row is not an agenda, which can be confirmed by the absence
        # of filesize text. Agenda.contents[2] is where the filesize is found.
        if agenda.contents[2].text:
            pdf_link = "http://www.normanok.gov" + agenda.a["href"]
            match = re.search(r'\d{1,4}-\d{1,2}-\d{1,2}', agenda.a.text)
            agenda_date = dparser.parse(match.group(0), fuzzy=True)
            agenda_title = agenda.a.text[match.end():len(agenda.a.text)].strip()
            agenda_obj = {
                "agenda_url": pdf_link,
                "agenda_date": agenda_date,
                "agenda_title": agenda_title,
                "pdf_link": pdf_link
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

def get_agenda_text(agenda_url):
    """
    This function takes an agenda URL and returns
    the PDF content converted to text.
    """
    agenda_text = pdf2text.convert_pdf(agenda_url)

    return agenda_text
