import re
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from council.crawlers.Crawler import Crawler

class TulsaCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("table")

    def get_page_source(self, url):
        browser = self.get_browser(url)
        timeout = 10
        try:
            # Tulsa uses iframes
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("iframe"))
            browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
            # Have to search by current month and year, so populate those in the form
            current_month = str(self.get_current_date().strftime("%B"))
            current_year = str(self.get_current_date().year)
            month_select = Select(browser.find_element_by_name("MeetingMonth"))
            month_select.select_by_visible_text(current_month)
            year_select = Select(browser.find_element_by_name("MeetingYear"))
            year_select.select_by_visible_text(current_year)
            # Submit search form
            browser.find_element_by_name("Submit").click()
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name("table"))
            # Get source of resulting search page
            page_source = browser.page_source
            browser.quit()
            return page_source
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        rows = parsed_html.find_all("td")
        for agenda in rows:
            if agenda.a:
                agenda_url = "http://legacy.tulsacouncil.org/inc/search/{}".format(agenda.a["href"])
                # Make sure agenda isn't already in the database
                if not self.agenda_exists(agenda_url):
                    match = re.search(r'\d{1,2}/\d{1,2}/\d{1,4}', agenda.text)
                    agenda_date = self.create_date(match.group(0))
                    # Make sure agenda isn't older than the cutoff date
                    if not self.too_old(agenda_date):
                        agenda_title = agenda.a.text
                        if self.name == "City Council":
                            self.name = "Council" # City Council agendas are labeled only as "Council"
                        # Check to see if agenda title matches the department
                        if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                            agenda_obj = {
                                "agenda_url": agenda_url,
                                "agenda_date": agenda_date,
                                "agenda_title": agenda_title,
                            }
                            filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        response = self.request(agenda.get("agenda_url"))
        soup = self.get_soup(response.text, "html.parser")
        agenda_text = soup.text.replace("â\x80\x99", "'").replace("BackupDocumentation", "").strip()
        agenda.update({
            "agenda_text": agenda_text,
            "pdf_link": ""
        })
        return agenda
