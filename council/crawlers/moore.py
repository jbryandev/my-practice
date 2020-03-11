"""
Crawler for the City of Moore. Moore agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class MooreCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("li", class_="public_meetings__meeting")
        soup = self.get_soup(response, "html.parser", parse_only=strainer)

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
        for agenda in soup.children:
            agenda_date = self.create_date(agenda.time.text)
            # Make sure agenda isn't older than the cutoff date
            if not self.too_old(agenda_date):
                # Check to see if agenda matches the department
                agenda_title = self.strip_title(agenda.a.text)
                if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                    # and it doesn't already exist in the database
                    agenda_url = self.get_agenda_url(agenda.a["href"])
                    if not self.agenda_exists(agenda_url) and agenda_url:
                        print("agenda doesn't already exist")
                        agenda = {
                            "agenda_date": agenda_date,
                            "agenda_title": agenda_title,
                            "agenda_url": agenda_url,
                            "pdf_link": agenda_url
                        }
                        agenda_list.append(agenda)

        return agenda_list

    def get_agenda_url(self, agenda_detail_url):
        response = self.get_url(agenda_detail_url)
        strainer = self.get_strainer("div", class_="accordion__item__content__wrapper")
        soup = self.get_soup(response, "html.parser", parse_only=strainer)
        if soup.a:
            agenda_url = soup.a["href"]
            return agenda_url
        else:
            return None

    def strip_title(self, agenda_title):
        # Remove "meeting" from end of title
        # match = re.search(r'Meeting', agenda_title)
        # if match:
        #     agenda_title = agenda_title[:match.start()-1]
        # Search for dash in title, and if found,
        # remove dash and everything before it
        match = re.search(r'-', agenda_title)
        if match:
            agenda_title = agenda_title[match.end()+1:]

        return agenda_title