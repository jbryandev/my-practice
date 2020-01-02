"""
Crawler for the City of Tulsa. Tulsa uses an online agenda system.
You have to search for agendas by month and year first, and then
it pulls up all of the agendas for that month/year combination.
This Crawler will uses Selenium to perform the search, and then
BeautifulSoup to extract the information. Agendas are in HTML, so
a PDF conversion is not necessary.
"""
from datetime import datetime
import re
import requests
import dateutil.parser as dparser
from bs4 import BeautifulSoup, SoupStrainer
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from ..modules import chromedriver

def retrieve_agendas(agendas_url):
    """
    This function takes a URL where the agendas can be found, and uses
    Selenium to perform the search on the main agenda page. The search
    will use the current month and year and will compile all agendas
    returned by the search.
    """
    print("Retrieving agendas...")
    print("Opening Chrome browser instance...")
    browser = chromedriver.open_browser(agendas_url)
    timeout = 20 # Set timeout length for WebDriverWait below
    agendas = ""
    try:
        WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("iframe"))
        browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
        current_month = str(datetime.now().strftime("%B"))
        current_year = str(datetime.now().year)
        month_select = Select(browser.find_element_by_name("MeetingMonth"))
        month_select.select_by_visible_text(current_month)
        year_select = Select(browser.find_element_by_name("MeetingYear"))
        year_select.select_by_visible_text(current_year)
        print("Submitting search form for current month and year...")
        browser.find_element_by_name("Submit").click()
        WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("table"))
        print("Scraping agendas table...")
        meeting_docs_table = SoupStrainer("table")
        soup = BeautifulSoup(browser.page_source, "html.parser", parse_only=meeting_docs_table)
        agendas = soup.find_all("td")
        print("Shutting down Chrome browser...")
        browser.quit()
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    agendas_list = []
    print("Processing scraped agendas...")
    for agenda in agendas:
        agenda_url = "http://www.tulsacouncil.org/inc/search/" + agenda.a["href"]
        match = re.search(r'\d{1,2}/\d{1,2}/\d{1,4}', agenda.text)
        agenda_date = dparser.parse(match.group(0), fuzzy=True)
        agenda_title = agenda.a.text
        agenda_obj = {
            "agenda_url": agenda_url,
            "agenda_date": agenda_date,
            "agenda_title": agenda_title,
        }
        agendas_list.append(agenda_obj)

    print("Processed " + str(len(agendas_list)) + " agendas.")
    return agendas_list

def match_agendas(agendas_list, department_name):
    """
    This function takes a BeautifulSoup ResultSet of scraped agendas, as well as the desired
    department name to match them against, and returns a set of only the agendas that match
    the corresponding department.
    """
    print("Looking for matching agendas...")
    matched_agendas = []
    if department_name == "City Council":
        department_name = "Council"
        # City Council agendas are labeled only as "Council"

    for agenda in agendas_list:
        if re.search(department_name, agenda.get("agenda_title")):
            print("Matching agenda found...")
            matched_agendas.append(agenda)

    print("Found " + str(len(matched_agendas)) + " matching agendas.")
    return matched_agendas

def get_agenda_content(agenda_url):
    """ This function takes an agenda URL and extracts the agenda contents. """
    response = requests.get(agenda_url)
    soup = BeautifulSoup(response.text, "html.parser")
    agenda_content = soup.text

    return agenda_content
