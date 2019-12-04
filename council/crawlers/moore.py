"""
Crawler for the City of Moore. Moore agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
# Import libraries
import dateparser
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4 import SoupStrainer
from council.modules import pdf2text

def retrieve_agendas(agendas_url):
    # This function takes a URL and retrieves all of the agendas
    # at this location. It returns a list of agenda objects.

    response = requests.get(agendas_url)
    agenda_li = SoupStrainer("li", class_="public_meetings__meeting")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_li)
    agenda_list = []
    for agenda in soup.children:
        agenda_date = agenda.time.text
        agenda_title = agenda.a.text
        agenda_subpage = agenda.a["href"]
        agenda_obj = {"agenda_date": agenda_date, "agenda_title": agenda_title, "agenda_subpage": agenda_subpage}
        agenda_list.append(agenda_obj)

    return agenda_list