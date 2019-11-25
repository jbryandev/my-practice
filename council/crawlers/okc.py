"""

"""
# Import libraries
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup, Tag, NavigableString

def scrape_agendas(agendas_url):
    # This function takes the URL where the agendas are located and returns
    # a BeautifulSoup object with the parsed HTML
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'
        })
    response = requests.get(agendas_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    agendas = soup.find_all("tr", "public_meeting", limit=5)
    for agenda in agendas:
        print(agenda.td)

