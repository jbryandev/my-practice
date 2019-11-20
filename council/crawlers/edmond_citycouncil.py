# Import libraries
import requests
from datetime import datetime
from django.utils.timezone import get_current_timezone
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4 import SoupStrainer

def edmond_city_council_crawler(agendas_url):

    # Connect to the agendas URL specified by the Department object
    response = requests.get(agendas_url)

    # Parse HTML and save to BeautifulSoup object
    agenda_table = SoupStrainer(class_="nowrap smallText") # parse only table of agendas
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_table)

    # Find all agendas matching agenda_name and add to database if not already added
    for tag in soup.find_all("td", string=agenda_name):
        # Select first child in tag, which contains all the agenda info we need
        agenda_info = tag.parent.select("td a")[0]

        # Convert agenda date string into datetime object
        agenda_date = datetime.strptime(str(agenda_info.string), "%B %d, %Y")

        # Store agenda url path
        agenda_url = "http://agenda.edmondok.com:8085/" + agenda_info['href']
    
        # Check to see if agenda is already in database
        if Agenda.objects.filter(agenda_url=agenda_url).exists():
            print("Agenda already exists! No need to add to database.")
        else:
            print("Agenda does not exist! Adding to database...")
            # Connect to the agenda URL and parse agenda HTML through BeautifulSoup
            response = requests.get(agenda_url)
            agenda_table = SoupStrainer("table") # parse only table tag
            soup = BeautifulSoup(response.text, "html.parser")

            # Find PDF link and save to variable
            agenda_pdf = "http://agenda.edmondok.com:8085" + soup.find("a", title="Download PDF Packet")['href']

            # Parse out agenda HTML and save as agenda text
            agenda_text_header = ""
            for string in soup.find("thead").contents[7].stripped_strings:
                agenda_text_header += string + "\n"
            agenda_text_body = ""
            for string in soup.find("tbody").stripped_strings:
                agenda_text_body += string + "\n"
            agenda_text = agenda_text_header + "\n" + agenda_text_body

            # Create new agenda object
            agenda = Agenda(
                    agenda_date=agenda_date,
                    agenda_title=agenda_name,
                    agenda_url=agenda_url,
                    agenda_text=agenda_text,
                    pdf_link=agenda_pdf,
                    date_added=datetime.now(tz=get_current_timezone()),
                    department=department
                )
            
            # Save new agenda to database
            agenda.save()
            print("Database update complete.")