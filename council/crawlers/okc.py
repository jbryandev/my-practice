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
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress
from council.modules import chromedriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import Tag

class OKCCrawler(Crawler):

    def crawl(self, progress_recorder):
        agenda_url = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid=5990&agviewdoctype=AGENDA"
        browser = self.open_browser(agenda_url)
        strainer = self.get_strainer("div")
        soup = self.get_soup(browser.page_source, "html.parser", parse_only=strainer)
        browser.quit()
        agenda_text = self.get_agenda_text(soup)
        agenda = {
            "agenda_date": self.get_current_date(),
            "agenda_title": "Test Agenda",
            "agenda_url": agenda_url,
            "agenda_text": agenda_text,
            "pdf_link": ""
        }
        new_agenda = self.create_new_agenda(agenda)
        new_agenda.save()

        # # Request City agenda website
        # set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        # browser = self.open_browser(self.url)
        # set_progress(progress_recorder, 1, 10, \
        #     "Connection succeeded. Getting current list of agendas...", 2)
        # strainer = self.get_strainer("tr", class_="public_meeting")
        # soup = self.get_soup(browser.page_source, "html.parser", parse_only=strainer)
        # browser.quit()

        # # Search agenda list for any new department agendas
        # status = "Searching list for any new {} agendas...".format(self.name)
        # set_progress(progress_recorder, 2, 10, status, 2)
        # agenda_list = self.get_agendas(soup)
        # status = "Found {} new agenda(s).".format(len(agenda_list))
        # set_progress(progress_recorder, 3, 10, status, 2)

        # # Loop over any new agendas, extract the agenda info, and save to database
        # i = 1
        # progress_step = 3
        # progress_length = len(agenda_list)*2 + 4
        # for agenda in agenda_list:
        #     # Get contents of agenda
        #     status = "Getting contents of agenda {} of {}...".format(i, len(agenda_list))
        #     progress_step += 1
        #     set_progress(progress_recorder, progress_step, progress_length, status, 2)
        #     print("AGENDA URL: {}".format(agenda.get("agenda_url")))
        #     browser = self.open_browser(agenda.get("agenda_url"))
        #     strainer = self.get_strainer("div")
        #     soup = self.get_soup(browser.page_source, "html.parser", parse_only=strainer)
        #     browser.quit()
        #     agenda_text = self.get_agenda_text(soup)

        #     # Get PDF link
        #     browser = self.open_browser(agenda.get("agenda_view_url"))
        #     strainer = self.get_strainer("table", id="tblMeetingDocs")
        #     soup = self.get_soup(browser.page_source, "html.parser", parse_only=strainer)
        #     browser.quit()
        #     pdf_link = ""
        #     if soup.a:
        #         pdf_link = "https://agenda.okc.gov/sirepub/{}".format(soup.a["href"])

        #     # Update agenda object with new info
        #     agenda.update({
        #         "agenda_text": agenda_text,
        #         "pdf_link": pdf_link
        #     })

        #     # Save agenda to database
        #     status = "Saving agenda {} of {} to the database...".format(i, len(agenda_list))
        #     progress_step += 1
        #     set_progress(progress_recorder, progress_step, progress_length, status, 2)
        #     new_agenda = self.create_new_agenda(agenda)
        #     new_agenda.save()
        #     i += 1

    def open_browser(self, url, timeout=10):
        browser = chromedriver.open_browser(url)
        try:
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
            return browser
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

    def get_agendas(self, soup):
        agenda_list = []
        # Limit search to 20 most-recent agendas
        rows = soup.find_all("tr", limit=20)
        for agenda in rows:
            # Split up agenda discription into string components
            agenda_strings = agenda.text.strip().split("\n")
            # Store date and title to vars
            agenda_date = self.create_date(agenda_strings[1].strip())
            agenda_title = agenda_strings[len(agenda_strings)-2].strip()
            # Check to see if agenda title matches the department
            if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                # Make sure agenda isn't older than the cutoff date
                if not self.too_old(agenda_date):
                    # Get more agenda details
                    agenda_links = agenda.find_all("a")
                    agenda_view_url = "https://agenda.okc.gov/sirepub/{}".format(agenda_links[0]["href"])
                    agenda_html_url = "https://agenda.okc.gov/sirepub/{}".format(agenda_links[1]["href"])
                    meeting_id = re.search(r'\d{4}', agenda_html_url).group(0)
                    agenda_url = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid={}&agviewdoctype=AGENDA".format(meeting_id)
                    # Make sure agenda isn't already in the database
                    if not self.agenda_exists(agenda_url):
                        agenda_obj = {
                            "agenda_date": agenda_date,
                            "agenda_title": agenda_title,
                            "agenda_url": agenda_url,
                            "agenda_view_url": agenda_view_url
                        }
                        agenda_list.append(agenda_obj)

        return agenda_list

    def get_agenda_text(self, soup):
        # The last item in soup.contents is the agenda text we want
        agenda_content = soup.contents[len(soup.contents)-1]
        strings = []
        # BS4 has trouble processing tables;
        # Loop over agenda content and fix the tables
        for row in agenda_content:
            if isinstance(row, Tag):
                col = row.find_all("td")
                if col:
                    if len(col) > 1:
                        if 100 < int(col[0]['width']) < 300:
                            strings.append("<tr><td style=\"width: 5%\"><td style=\"width: 5%\"></td></td><td style=\"width: 5%\">{}</td><td>{}\n\n</td></tr>".format(
                                col[0].text.strip(), col[1].text.strip()))
                        elif 60 < int(col[0]['width']) < 100:
                            strings.append("<tr><td style=\"width: 5%\"></td><td style=\"width: 5%\">{}</td><td colspan=\"2\">{}\n\n</td></tr>".format(
                                col[0].text.strip(), col[1].text.strip()))
                        elif int(col[0]['width']) < 60:
                            strings.append("<tr><td style=\"width: 5%\">{}</td><td colspan=\"3\">{}\n\n</td></tr>".format(col[0].text.strip(), col[1].text.strip()))
                    else:
                        strings.append("<tr><td colspan=\"4\">{}\n\n</td></tr>".format(col[0].text.strip()))
                else:
                    strings.append("<tr><td colspan=\"4\">{}\n\n</td></tr>".format(row.text.strip().replace('\n', '').replace('\xa0', '')))
        # Join the rows of body text together into one string, and then put the header and body
        # text together to create agenda_text
        body = "".join(strings)
        agenda_text = "<table>{}</table>".format(body)
        return agenda_text

# import re
# import dateutil.parser as dparser
# from bs4 import BeautifulSoup, SoupStrainer
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import TimeoutException
# from ..modules import chromedriver

# def retrieve_agendas(agendas_url):
#     """
#     This function takes the URL where the agendas are located and returns a BeautifulSoup ResultSet
#     limited to the most recent 20 agendas found (of all departments)
#     """
#     print("Retrieving agendas...")
#     browser = chromedriver.open_browser(agendas_url)
#     timeout = 20 # Set timeout length for WebDriverWait below
#     try:
#         WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
#         soup = BeautifulSoup(browser.page_source, 'html.parser')
#         agendas_list = soup.find_all("tr", "public_meeting", limit=20)
#         browser.quit()
#     except TimeoutException:
#         print("Timed out waiting for page to load")
#         browser.quit()

#     if not agendas_list:
#         print("Error: unable to retrieve any agendas.")
#     else:
#         print(str(len(agendas_list)) + " agendas retrieved.")
#         return agendas_list

# def match_agendas(agendas_list, department_name):
#     """
#     This function takes a BeautifulSoup ResultSet of scraped agendas, as well as the desired
#     department name to match them against, and returns a set of only the agendas that match
#     the corresponding department.
#     """
#     print("Looking for matching agendas...")
#     matched_agendas = []
#     for agenda in agendas_list:
#         agenda_string = str(agenda.td.text).strip()
#         # Split string on linespaces
#         agenda_string_split = agenda_string.split("\n")
#         # Delete "View" text from string
#         agenda_string_split.pop(0)
#         # Delete "Agenda" leaving only date, time, name
#         agenda_string_split.pop(len(agenda_string_split)-1)
#         # Get name, which is last string
#         agenda_name = agenda_string_split[len(agenda_string_split)-1].strip()
#         # If the agenda matches the desired department, then process it
#         if agenda_name == department_name:
#             agenda_date = dparser.parse(agenda_string_split[0].strip(), fuzzy=True)
#             agenda_links = agenda.td.find_all("a")
#             agenda_view_link = "https://agenda.okc.gov/sirepub/" + agenda_links[0]["href"]
#             meeting_id = re.search(r'\d{4}', agenda_links[1]["href"]).group(0)
#             agenda_path = "https://agenda.okc.gov/sirepub/agview.aspx?agviewmeetid=" \
#                 + meeting_id + "&agviewdoctype=AGENDA"
#             agenda_obj = {
#                 "agenda_date": agenda_date,
#                 "agenda_title": agenda_name,
#                 "agenda_url": agenda_path,
#                 "agenda_view_link": agenda_view_link
#             }
#             print("Agenda match found: " + str(agenda_date) + " " + agenda_name)
#             matched_agendas.append(agenda_obj)
#         else:
#             print("No agenda matches found.")

#     return matched_agendas

# def get_agenda_text(agenda_url):
#     """
#     This function takes a URL of the desired agenda to scrape and uses Selenium
#     to open the page and BeautifulSoup to scrape the contents.
#     It returns a BeautifulSoup object of the agenda content.
#     """
#     print("Attempting to get agenda content...")
#     agenda_text = ""
#     browser = chromedriver.open_browser(agenda_url)
#     timeout = 20 # Set timeout length for WebDriverWait below
#     try:
#         WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
#         agenda_soup = BeautifulSoup(browser.page_source, 'html.parser')
#         for div in agenda_soup.find_all("div"):
#             agenda_text += div.text  + "\n"
#         browser.quit()
#     except TimeoutException:
#         print("Timed out waiting for page to load")
#         browser.quit()

#     return agenda_text

# def get_agenda_pdf(agenda_view_link):
#     """
#     This functions takes a URL of the agenda view summary page
#     and extracts the URL for the agenda PDF document.
#     """
#     browser = chromedriver.open_browser(agenda_view_link)
#     timeout = 20 # Set timeout length for WebDriverWait below
#     try:
#         WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
#         meeting_docs_table = SoupStrainer("table", id="tblMeetingDocs")
#         soup = BeautifulSoup(browser.page_source, "html.parser", parse_only=meeting_docs_table)
#         pdf_link = "https://agenda.okc.gov/sirepub/" + soup.a["href"]
#         browser.quit()
#     except TimeoutException:
#         print("Timed out waiting for page to load")
#         browser.quit()

#     return pdf_link
