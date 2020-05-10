import re, unicodedata
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import Tag
from council.modules.Crawler import Crawler

class OKCCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("tr", class_="public_meeting")

    def get_page_source(self, url):
        self.progress_recorder.update(1, 20, "Opening browser instance...")
        browser = self.get_browser(url)
        timeout = 10
        try:
            WebDriverWait(browser, timeout).until(lambda x: x.find_element_by_tag_name('body'))
            page_source = browser.page_source
            browser.quit()
            return page_source
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        # Limit search to 50 most-recent agendas
        rows = parsed_html.find_all("tr", limit=50)
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
                        filtered_agendas.append(agenda_obj)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # Get contents of agenda
        browser = self.get_browser(agenda.get("agenda_url"))
        self.set_strainer("table", class_="MsoNormalTable")
        soup = self.get_soup(browser.page_source, "html.parser", parse_only=self.strainer)
        if not soup.text:
            soup = self.get_soup(browser.page_source, "html.parser")
        browser.quit()
        agenda_text = self.get_agenda_text(soup)
        if "cancellation notice" in agenda_text.lower():
            agenda.update({
                "agenda_title": str(agenda.get("agenda_title")) + " (Cancelled)"
            })

        # Get PDF link
        browser = self.get_browser(agenda.get("agenda_view_url"))
        self.set_strainer("table", id="tblMeetingDocs")
        source = browser.page_source.encode(encoding='UTF-8')
        soup = self.get_soup(source, "html.parser", parse_only=self.strainer)
        browser.quit()
        pdf_link = ""
        if soup.a:
            pdf_link = "https://agenda.okc.gov/sirepub/{}".format(soup.a["href"])

        # Update agenda object with new info
        agenda.update({
            "agenda_text": agenda_text,
            "pdf_link": pdf_link
        })
        return agenda

    @staticmethod
    def get_agenda_text(soup):
        strings = []
        # BS4 has trouble processing tables;
        # Loop over agenda content and fix the tables
        for row in soup.contents:
            if isinstance(row, Tag):
                col = row.find_all("td")
                if col:
                    if len(col) > 1:
                        if int(col[0]['width']) > 300:
                            strings.append("<div>{}</div>\n<div class=\"mb-3\">{}</div>\n\n".format(
                                col[0].text.strip(), col[1].text.strip().replace("\n", "").replace("\xa0", " ")))
                        elif 100 < int(col[0]['width']) < 300:
                            strings.append("<div class=\"mb-3\" style=\"padding-left: 0.50in\">{} {}</div>\n\n".format(
                                col[0].text.strip(), col[1].text.strip().replace("\n", "").replace("\xa0", " ")))
                        elif 60 < int(col[0]['width']) < 100:
                            strings.append("<div class=\"mb-3\" style=\"padding-left: 0.25in\">{} {}</div>\n\n".format(
                                col[0].text.strip(), col[1].text.strip().replace("\n", "").replace("\xa0", " ")))
                        elif int(col[0]['width']) < 60:
                            strings.append("<div class=\"mb-3\">{} {}</div>\n\n".format(
                                col[0].text.strip(), col[1].text.strip().replace("\n", "").replace("\xa0", " ")))
                    else:
                        if col[0].text.strip():
                            strings.append("<div class=\"mb-3\">{}</div>\n\n".format(
                                col[0].text.strip().replace("\n", "").replace("\xa0", " ")))
                else:
                    strings.append("<div>{}</div>\n\n".format(
                        row.text.strip().replace("\xa0", " ").replace('\n', '<br>')))
        # Join the rows of body text together into one string
        agenda_text = "".join(strings)
        return agenda_text
