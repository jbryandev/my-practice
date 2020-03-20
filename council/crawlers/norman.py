"""
Crawler for the City of Norman. Norman agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class NormanCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("table", id="filebrowser-file-listing")
        soup = self.get_soup(response.text, "html.parser", parse_only=strainer)

        # Search agenda list for any new department agendas
        status = "Searching list for any new {} agendas...".format(self.name)
        set_progress(progress_recorder, 2, 10, status, 2)
        agenda_list = self.get_agendas(soup)
        status = "Found {} new agenda(s).".format(len(agenda_list))
        set_progress(progress_recorder, 3, 10, status, 2)

        # For each new agenda found, add it to the database
        i = 1
        progress_step = 3
        progress_length = len(agenda_list) + 4
        for agenda in agenda_list:
            status = "Saving agenda {} of {} to the database...".format(i, len(agenda_list))
            progress_step += 1
            set_progress(progress_recorder, progress_step, progress_length, status, 2)
            new_agenda = self.create_new_agenda(agenda)
            new_agenda.save()
            i += 1

    def get_agendas(self, soup):
        agenda_list = []
        # Limit search to 5 most-recent agendas
        rows = soup.tbody.find_all("tr", limit=5)
        for agenda in rows:
            # The first row is not an agenda, which can be confirmed by the absence
            # of filesize text. Agenda.contents[2] is where the filesize is found.
            if agenda.contents[2].text:
                agenda_url = "http://www.normanok.gov{}".format(agenda.a["href"])
                # Make sure agenda isn't already in the database
                if not self.agenda_exists(agenda_url):
                    # Separate out date and title
                    match = re.search(r'\d{1,4}-\d{1,2}-\d{1,2}', agenda.a.text)
                    agenda_date = self.create_date(match.group(0))
                    agenda_title = agenda.a.text[match.end():len(agenda.a.text)].strip()
                    # Check to see if agenda title matches the department
                    if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                        # Make sure agenda isn't older than the cutoff date
                        if not self.too_old(agenda_date):
                            agenda_obj = {
                                "agenda_date": agenda_date,
                                "agenda_title": agenda_title,
                                "agenda_url": agenda_url,
                                "pdf_link": agenda_url
                            }
                            agenda_list.append(agenda_obj)

        return agenda_list