"""
Crawler for the City of Lawton. Lawton agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.

Lawton lists past agendas at a different link, so we don't need to worry
about checking if any agendas are older than the cutoff date.
"""
import re
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class LawtonCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("article")
        soup = self.get_soup(response, "html.parser", parse_only=strainer)

        # Search agenda list for any new department agendas
        status = "Searching list for any new {} agendas...".format(self.name)
        set_progress(progress_recorder, 2, 10, status, 2)
        agenda_list = self.get_agendas(soup)
        status = "Found {} new agenda(s).".format(len(agenda_list))
        set_progress(progress_recorder, 3, 10, status, 2)

        # For each new agenda found, open its corresponding detail page
        # to extract the agenda PDF link, then save agenda to database
        i = 1
        progress_step = 3
        progress_length = len(agenda_list)*2 + 4
        for agenda in agenda_list:
            # Get contents of agenda
            status = "Getting details for agenda {} of {}...".format(i, len(agenda_list))
            progress_step += 1
            set_progress(progress_recorder, progress_step, progress_length, status, 2)
            response = self.get_url(agenda.get("agenda_url"))
            strainer = self.get_strainer("span", class_="file-link")
            soup = self.get_soup(response, "html.parser", parse_only=strainer)
            pdf_link = soup.a["href"]
            agenda.update({"pdf_link": pdf_link})

            # Save agenda to database
            status = "Saving agenda {} of {} to the database...".format(i, len(agenda_list))
            progress_step += 1
            set_progress(progress_recorder, progress_step, progress_length, status, 2)
            new_agenda = self.create_new_agenda(agenda)
            new_agenda.save()
            i += 1

    def get_agendas(self, soup):
        agenda_list = []
        for agenda in soup.children:
            agenda_title = agenda.h3.text.strip()
            # If agenda title matches the current department...
            if agenda_title.lower() == self.name.lower():
                # And if the agenda is available...
                match = re.search("Agenda Available", agenda.text)
                if match:
                    # Store agenda information and append to agenda list
                    agenda_day = agenda.select(".event-card-day")[0].text
                    agenda_month = agenda.select(".event-card-year")[0].text
                    agenda_date = self.create_date("{} {}".format(agenda_day, agenda_month))
                    agenda_url = "https://www.lawtonok.gov{}".format(agenda["about"])
                    agenda_obj = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title,
                        "agenda_url": agenda_url
                    }
                    agenda_list.append(agenda_obj)

        return agenda_list
