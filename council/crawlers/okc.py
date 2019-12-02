"""
Crawler for the City of Oklahoma City. OKC uses an online meeting agenda system,
and agendas are presented in HTML format with a link to download as a PDF.
This crawler will read the HTML agenda, since that will be more reliable
than using OCR to convert the PDF to text.

Since all agendas are posted to the online system, this crawler can be
used to handle any City department, as the extraction method will be
the same.
"""
# Import libraries
import dateutil.parser as dparser
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup, Tag, NavigableString

def scrape_agendas(agendas_url, department_name):
    # This function takes the URL where the agendas are located and returns
    # a BeautifulSoup object with the parsed HTML
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'
        })
    agendas_url = "https://agenda.okc.gov/sirepub/meet.aspx"
    department_name = "City Council"
    response = requests.get(agendas_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    agendas = soup.find_all("tr", "public_meeting", limit=10) # There are hundreds of agendas on this page, hence the limit
    for agenda in agendas:
        agenda_string = str(agenda.td.text).strip()
        agenda_string_split = agenda_string.split("\r\n") # Split string on linespaces
        agenda_string_split.pop(0) # Delete "View" text from string
        agenda_string_split.pop(len(agenda_string_split)-1) # Delete "Agenda" leaving only date, time, name
        agenda_name = agenda_string_split[len(agenda_string_split)-1].strip()
        if agenda_name == department_name:
            agenda_date = dparser.parse(agenda_string_split[0].strip(), fuzzy=True)
            agenda_links = agenda.td.find_all("a")
            meeting_id = re.search('\d{4}', agenda_links[1]["href"]).group(0)
            agenda_path = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid=" + meeting_id + "&agviewdoctype=AGENDA"
            response = requests.get(agenda_path, headers=headers)
            agenda_soup = BeautifulSoup(response.text, "html.parser")
            print(agenda_soup) # DEAD END, HEADERS NOT WORKING
            agenda_text = ""
            for string in agenda_soup.find("body").stripped_strings:
                agenda_text += string
            print(agenda_text)
    return agendas

