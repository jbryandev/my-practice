"""
Crawler for the City of Edmond. Edmond uses an online meeting agenda system,
and agendas are presented in HTML format with a link to download as a PDF.
This crawler will read the HTML agenda, since that will be more reliable
than using OCR to convert the PDF to text.

Since all agendas are posted to the online system, this crawler can be
used to handle any City department, as the extraction method will be
the same.
"""
# Import libraries
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4 import SoupStrainer
from ..models import Agenda, Department

def retrieve_current_agendas(agendas_url):
    # This function takes the URL where the agendas are located and returns
    # a BeautifulSoup object with the parsed HTML
    
    response = requests.get(agendas_url)
    
    # Don't need entire HTML page, just parse only TABLE tag containing the agendas
    agendas_table = SoupStrainer(class_="nowrap smallText")
    
    return BeautifulSoup(response.text, "html.parser", parse_only=agendas_table)

def find_specific_agendas(parsed_html, agenda_name):
    # This function takes a BeautifulSoup object containing parsed HTML and
    # the agenda name to search for, and returns a list of matching agendas.
    # The resulting list will contain key value pairs of the agenda date as
    # a datetime object and the agenda URL as a string.
    
    agenda_set = []
    
    for tag in parsed_html.find_all("td", string=re.compile("%s" % agenda_name)):
        
        # Select first child in tag, which contains all the agenda info we need
        agenda_info = tag.parent.select("td a")[0]
        
        # Convert agenda date string into datetime object
        agenda_date = datetime.strptime(str(agenda_info.string), "%B %d, %Y")

        # Clean up agenda url path
        agenda_url = "http://agenda.edmondok.com:8085/" + agenda_info['href']

        agenda = {"agenda_date": agenda_date, "agenda_url": agenda_url}

        agenda_set.append(agenda)
    
    return agenda_set

def agenda_exists(agenda_url):
    # This function takes an agenda URL and makes sure that it is not
    # already associated with an agenda in the database
     
    if Agenda.objects.filter(agenda_url=agenda_url).exists():
        
        return True
    
    else:

        return False

def get_agenda(agenda_url):
    # This function takes an agenda URL and extracts the agenda contents.
                   
    # Connect to the agenda URL and parse agenda HTML through BeautifulSoup
    response = requests.get(agenda_url)
    agenda_table = SoupStrainer("table") # parse only TABLE tag
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find PDF link (if available) and save to variable
    download_link = soup.find("a", title="Download PDF Packet")
    agenda_pdf = ""
    if download_link:
        agenda_pdf = "http://agenda.edmondok.com:8085" + download_link['href']
    
    # Parse out agenda HTML and save as agenda text
    
    agenda_text_header = ""
    
    for string in soup.find("thead").contents[7].stripped_strings:
        
        agenda_text_header += string + "\n"
    
    agenda_text_body = ""
    
    for string in soup.find("tbody").stripped_strings:
        
        agenda_text_body += string + "\n"
    
    agenda_text = agenda_text_header + "\n" + agenda_text_body

    agenda = {"agenda_url": agenda_url, "pdf_link": agenda_pdf, "agenda_text": agenda_text}

    return agenda

def fetch_agendas(agendas_url, agenda_name):
    # This function combines all of the methods above to retrieve a list of new agendas
    # ready to be added to the database for a particular department
    # It returns a list of Agenda objects (minus the department and date added fields)

    agenda_html = retrieve_current_agendas(agendas_url)

    specific_agendas = find_specific_agendas(agenda_html, agenda_name)

    new_agendas = []

    for agenda in specific_agendas:

        agenda_url = agenda.get("agenda_url")
        
        if not agenda_exists(agenda_url):

            parsed_agenda = get_agenda(agenda_url)
            parsed_agenda.update({"agenda_date": agenda.get("agenda_date"), "agenda_name": agenda_name})
            
            new_agenda = Agenda(
                agenda_date=parsed_agenda.get("agenda_date"),
                agenda_title=parsed_agenda.get("agenda_name"),
                agenda_url=parsed_agenda.get("agenda_url"),
                agenda_text=parsed_agenda.get("agenda_text"),
                pdf_link=parsed_agenda.get("pdf_link"),
            )

            new_agendas.append(new_agenda)

    return new_agendas