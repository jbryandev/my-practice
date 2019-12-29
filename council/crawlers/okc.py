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
import re
import dateutil.parser as dparser
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from ..modules import chromedriver

def retrieve_agendas(agendas_url):
    """
    This function takes the URL where the agendas are located and returns a BeautifulSoup ResultSet
    limited to the most recent 20 agendas found (of all departments)
    """
    print("Retrieving agendas...")
    browser = open_browser(agendas_url)
    timeout = 20 # Set timeout length for WebDriverWait below
    try:
        WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        agendas_list = soup.find_all("tr", "public_meeting", limit=20)
        browser.quit()
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    if not agendas_list:
        print("Error: unable to retrieve any agendas.")
    else:
        print(str(len(agendas_list)) + " agendas retrieved.")
        return agendas_list

def match_agendas(agendas_list, department_name):
    """
    This function takes a BeautifulSoup ResultSet of scraped agendas, as well as the desired
    department name to match them against, and returns a set of only the agendas that match
    the corresponding department.
    """
    print("Looking for matching agendas...")
    matched_agendas = []
    for agenda in agendas_list:
        agenda_string = str(agenda.td.text).strip()
        # Split string on linespaces
        agenda_string_split = agenda_string.split("\n")
        # Delete "View" text from string
        agenda_string_split.pop(0)
        # Delete "Agenda" leaving only date, time, name
        agenda_string_split.pop(len(agenda_string_split)-1)
        # Get name, which is last string
        agenda_name = agenda_string_split[len(agenda_string_split)-1].strip()
        # If the agenda matches the desired department, then process it
        if agenda_name == department_name:
            agenda_date = dparser.parse(agenda_string_split[0].strip(), fuzzy=True)
            agenda_links = agenda.td.find_all("a")
            agenda_view_link = "https://agenda.okc.gov/sirepub/" + agenda_links[0]["href"]
            meeting_id = re.search(r'\d{4}', agenda_links[1]["href"]).group(0)
            agenda_path = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid=" \
                + meeting_id + "&agviewdoctype=AGENDA"
            agenda_obj = {
                "agenda_date": agenda_date,
                "agenda_title": agenda_name,
                "agenda_url": agenda_path,
                "agenda_view_link": agenda_view_link
            }
            print("Agenda match found: " + str(agenda_date) + " " + agenda_name)
            matched_agendas.append(agenda_obj)
        else:
            print("No agenda matches found.")

    return matched_agendas

def get_agenda_text(agenda_url):
    """
    This function takes a URL of the desired agenda to scrape and uses Selenium
    to open the page and BeautifulSoup to scrape the contents.
    It returns a BeautifulSoup object of the agenda content.
    """
    print("Attempting to get agenda content...")
    agenda_text = ""
    browser = open_browser(agenda_url)
    timeout = 20 # Set timeout length for WebDriverWait below
    try:
        WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
        agenda_soup = BeautifulSoup(browser.page_source, 'html.parser')
        for div in agenda_soup.find_all("div"):
            agenda_text += div.text  + "\n"
        browser.quit()
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    return agenda_text

def get_agenda_pdf(agenda_view_link):
    """
    This functions takes a URL of the agenda view summary page
    and extracts the URL for the agenda PDF document.
    """
    browser = open_browser(agenda_view_link)
    timeout = 20 # Set timeout length for WebDriverWait below
    try:
        WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
        meeting_docs_table = SoupStrainer("table", id="tblMeetingDocs")
        soup = BeautifulSoup(browser.page_source, "html.parser", parse_only=meeting_docs_table)
        pdf_link = "https://agenda.okc.gov/sirepub/" + soup.a["href"]
        browser.quit()
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()

    return pdf_link

def open_browser(page_url):
    """
    This function uses Selenium to open a Chrome browser instance and
    navigate to the given URL.
    """
    print("open_browser called")
    chrome_options = chromedriver.set_chrome_options()
    browser = chromedriver.get_chrome_driver(chrome_options)
    browser.get(page_url)

    return browser
