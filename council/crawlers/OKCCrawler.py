import re, json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from council.modules.Crawler import Crawler

# Crawler for new OKC City Council agenda portal
class OKCCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        # self.set_strainer("div", class_="content public_portal_search bodyBackgroundColour bodyTextFont")

    def get_page_source(self, url):
        # browser = webdriver.PhantomJS()
        # browser.get(url)
        # timeout = 10
        # try:
        #     WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
        #     page_source = browser.page_source
        #     browser.quit()
        #     return page_source
        # except TimeoutException:
        #     print("Timed out waiting for page to load")
        #     browser.quit()

        # Get JSON data directly
        json_path = "https://okc.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings"
        request = self.request(json_path)
        return request.text

    def parse_html(self, page_source):
        json_data = json.loads(page_source)
        return json_data

    def filter_agendas(self, json_data):
        filtered_agendas = []
        for agenda in json_data:
            agenda_title = agenda.get("title")
            agenda_date = self.create_date(agenda.get("date"))
            # Check title matches department & agenda isn't too old
            if re.search(self.name.lower().strip(), agenda_title.lower().strip()) and \
                not self.too_old(agenda_date):
                agenda_id = agenda.get("documentList")[0].get("id")
                file_id = agenda.get("documentList")[1].get("id")
                agenda_url = "https://okc.primegov.com/Portal/Meeting?compiledMeetingDocumentFileId={}".format(agenda_id)
                pdf_link = "https://okc.primegov.com/Public/CompiledDocument/{}".format(file_id)
                # pdf_link_url = "https://okc.primegov.com/api/Meeting/getcompiledfiledownloadurl?compiledFileId={}".format(file_id)
                # Make sure agenda isn't already in the database
                if not self.agenda_exists(agenda_url):
                    # Save to agenda object
                    agenda_obj = {
                            "agenda_date": agenda_date,
                            "agenda_title": agenda_title,
                            "agenda_url": agenda_url,
                            "pdf_link": pdf_link
                        }
                    filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # Get contents of agenda
        page_source = self.request(agenda.get("agenda_url"))
        soup = self.get_soup(page_source.text, "html.parser")      
        agenda_text = self.get_agenda_text(soup)
        # Update agenda object with new info
        agenda.update({
            "agenda_text": agenda_text,
        })
        return agenda

    def get_agenda_text(self, soup):
        # Get list of all tables containing agenda items
        agenda_item_tables = soup.find_all("table", style="width:100%;")
        strings = []
        for table in agenda_item_tables:
            # Find section row
            if table.find("tr", class_="section-row"):
                strings.append("<div class=\"mb-3\">{}</div>\n\n".format(
                    table.find("tr", class_="section-row").text.strip().replace("\n", " ").replace("\xa0", " ").replace("\t", " ")))
            # Find any meeting items
            meeting_items = table.find_all("div", class_="meeting-item")
            for item in meeting_items:
                strings.append("<div class=\"mb-3\" style=\"padding-left: 0.25in\">{}</div>\n\n".format(
                    item.text.strip().replace("\n", " ").replace("\xa0", " ").replace("\t", " ")))
        agenda_text = "".join(strings)
        return agenda_text
