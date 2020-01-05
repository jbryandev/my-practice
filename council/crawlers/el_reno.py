"""
Crawler for the City of El Reno. El Reno agendas are only available as
a scanned PDF, therefore, OCR must be used to convert the PDF to text.

"""
from datetime import datetime
import re
import dateparser
import requests
from django.utils.timezone import get_current_timezone
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

def retrieve_agendas(agendas_url):
    """
    This function takes the URL where the agendas are located and returns a
    BeautifulSoup ResultSet object with the parsed HTML of all agendas listed.
    """
    response = requests.get(agendas_url)
    # Parse only the div tag that contains all of the agendas
    agenda_div = SoupStrainer("div", class_="grid-9")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_div)
    all_agendas = soup.find_all("li") # Retrieves all agendas on the page

    # Trim out only the current year agendas
    agenda_list = []
    current_year = str(datetime.now().year)
    for agenda in all_agendas:
        # Regex that searches for current year in the URL path
        if re.search(current_year, agenda.a["href"]):
            agenda_list.append(agenda)
    return agenda_list

def get_most_recent_agendas(agenda_list):
    """
    This function takes a BeautifulSoup ResultSet and finds the 5 most recent agendas.
    It returns a list of BeautifulSoup Tag objects containing the agendas.
    """
    tag_list = []
    i = 1
    while i <= 5 and i <= len(agenda_list):
        tag_list.append(agenda_list[len(agenda_list) - i])
        i += 1

    return tag_list

def parse_agenda_info(agenda):
    """
    This function takes a BeautifulSoup Tag Object and parses out the
    relevant agenda information, then returns a list of key-value pairs
    """
    # Store agenda URL
    agenda_url = agenda.a["href"]
    # Get agenda title as a string
    agenda_string = agenda.a.string

    # Test if agenda title contains letters
    match = re.search('[a-zA-Z]', agenda_string)
    agenda_date = ""
    agenda_name = ""
    if match:
        # Agenda title contains letters (date & title)
        # Separate date from title
        match = re.search(r'\d{1,2}-\d{1,2}-\d{1,2}', agenda_string)
        if match:
            agenda_date = agenda_string[match.start():match.end()]
            agenda_name = agenda_string.replace(
                agenda_string[match.start():match.end()], "").strip()
        else:
            agenda_date = datetime.now(tz=get_current_timezone()).strftime("%m/%d/%Y")
            agenda_name = agenda_string
    else:
        # Agenda title does not contain letters (date only)
        agenda_date = agenda_string

    # Convert agenda date to datetime object
    agenda_date = dateparser.parse(agenda_date)

    # Store all the agenda info as key value pairs
    agenda_info = {
        "agenda_date": agenda_date,
        "agenda_title": agenda_name,
        "agenda_url": agenda_url,
        "agenda_text": "", # will be generated upon user request
        "pdf_link": agenda_url, # in this case it's the same as the agenda URL
        }

    return agenda_info
