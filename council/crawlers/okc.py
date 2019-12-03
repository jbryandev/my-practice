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
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4 import SoupStrainer
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

def retrieve_agendas(agendas_url):
    # This function takes the URL where the agendas are located and returns a BeautifulSoup ResultSet
    # limited to the most recent 20 agendas found (of all departments)

    # OKC agenda website protects against robots, so headers need to be spoofed
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'
        })
    agendas_url = "https://agenda.okc.gov/sirepub/meet.aspx" #temporary for testing
    response = requests.get(agendas_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    agendas_list = soup.find_all("tr", "public_meeting", limit=20) # There are hundreds of agendas on this page, hence the limit

    return agendas_list

def match_agendas(agendas_list, department_name):
    # This function takes a BeautifulSoup ResultSet of scraped agendas, as well as the desired
    # department name to match them against, and returns a set of only the agendas that match
    # the corresponding department
    matched_agendas = []
    department_name = "City Council" # temporary for testing
    for agenda in agendas_list:
        agenda_string = str(agenda.td.text).strip()
        agenda_string_split = agenda_string.split("\r\n") # Split string on linespaces
        agenda_string_split.pop(0) # Delete "View" text from string
        agenda_string_split.pop(len(agenda_string_split)-1) # Delete "Agenda" leaving only date, time, name
        agenda_name = agenda_string_split[len(agenda_string_split)-1].strip() # Get name, which is last string
        
        # If the agenda matches the desired department, then process it
        if agenda_name == department_name:
            agenda_date = dparser.parse(agenda_string_split[0].strip(), fuzzy=True)
            agenda_links = agenda.td.find_all("a")
            agenda_view_link = "https://agenda.okc.gov/sirepub/" + agenda_links[0]["href"]
            meeting_id = re.search('\d{4}', agenda_links[1]["href"]).group(0)
            agenda_path = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid=" + meeting_id + "&agviewdoctype=AGENDA"
            agenda_obj = {"agenda_date": agenda_date, "agenda_title": agenda_name, "agenda_url": agenda_path, "agenda_view_link": agenda_view_link}
            matched_agendas.append(agenda_obj)
        
    return matched_agendas
            
def get_agenda_text(agenda_url):
    # This function takes a URL of the desired agenda to scrape and uses Selenium to open the page
    # and BeautifulSoup to scrape the contents. It returns a BeautifulSoup object of the agenda content. 
      
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
    # This functions takes a URL of the agenda view summary page
    # and extracts the URL for the agenda PDF document

    # OKC agenda website protects against robots, so headers need to be spoofed
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'
        })
    response = requests.get(agenda_view_link, headers=headers)
    meeting_docs_table = SoupStrainer("table", id="tblMeetingDocs")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=meeting_docs_table)
    pdf_link = "https://agenda.okc.gov/sirepub/" + soup.a["href"]
    
    return pdf_link

def open_browser(page_url):
    # This function uses Selenium to open a Chrome browser instance and navigate to the given URL

    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False); # prevents unpacked extensions error dialog box from popping up
    browser = webdriver.Chrome(
        executable_path=r"C:\\Users\\james.bryan\AppData\\Local\\Programs\\Python\\Python37-32\\Lib\\site-packages\\selenium\\webdriver\\chrome\\chromedriver",
        chrome_options=options
        )
    browser.get(page_url)

    return browser