"""
Crawler for the City of Edmond. Edmond uses an online meeting agenda system,
and agendas are presented in HTML format with a link to download as a PDF.
This crawler will read the HTML agenda, since that will be more reliable
than using OCR to convert the PDF to text.

Since all agendas are posted to the online system, this crawler can be
used to handle any City department, as the extraction method will be
the same.
"""
import re
import requests
import dateutil.parser as dparser
from bs4 import BeautifulSoup, SoupStrainer

def retrieve_current_agendas(agendas_url):
    """
    This function takes the URL where the agendas are located and returns
    a BeautifulSoup object with the parsed HTML
    """
    response = requests.get(agendas_url)
    # Don't need entire HTML page, just parse only TABLE tag containing the agendas
    agendas_table = SoupStrainer(class_="nowrap smallText")

    return BeautifulSoup(response.text, "html.parser", parse_only=agendas_table)

def find_specific_agendas(parsed_html, agenda_name):
    """
    This function takes a BeautifulSoup object containing parsed HTML and
    the agenda name to search for, and returns a list of matching agendas.
    The resulting list will contain key value pairs of the agenda date as
    a datetime object and the agenda URL as a string.
    """
    agenda_set = []
    for tag in parsed_html.find_all("td", string=re.compile("%s" % agenda_name)):
        # Select first child in tag, which contains all the agenda info we need
        agenda_info = tag.parent.td

        # Convert agenda date string into datetime object
        agenda_date = dparser.parse(agenda_info.text, fuzzy=True)

        # Check for existence of agenda link and create agenda object if exists
        if agenda_info.a:
            agenda_url = "http://agenda.edmondok.com:8085/" + agenda_info.a['href']
            agenda = {"agenda_date": agenda_date, "agenda_url": agenda_url}
            agenda_set.append(agenda)

    return agenda_set

def get_agenda(agenda_url):
    """ This function takes an agenda URL and extracts the agenda contents. """
    # Connect to the agenda URL and parse agenda HTML through BeautifulSoup
    response = requests.get(agenda_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find PDF link (if available) and save to variable
    download_link = soup.find("a", title="Download PDF Packet")
    agenda_pdf = ""
    if download_link:
        agenda_pdf = "http://agenda.edmondok.com:8085" + download_link['href']

    # Parse out agenda HTML and save as agenda text
    rows = soup.find_all("tr")
    agenda_text = ""
    i = 3
    while i < len(rows):
        agenda_text += (rows[i].text.strip() + "\n")
        i += 1

    agenda = {"agenda_url": agenda_url, "pdf_link": agenda_pdf, "agenda_text": agenda_text}

    return agenda
