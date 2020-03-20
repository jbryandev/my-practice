"""
Crawler for the City of El Reno. El Reno agendas are only available as
a scanned PDF, therefore, OCR must be used to convert the PDF to text.

"""
import re
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class ElRenoCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("div", class_="javelin_regionContent")
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
        # Current year agendas SHOULD be found at soup.contents[1].contents[3]
        # This is the first group of agendas at the top of the agenda page
        current_year_agendas = soup.contents[1].contents[3].find_all("li")

        # Loop over current year agendas and weed out
        for agenda in current_year_agendas:
            agenda_url = agenda.a["href"]

            # Check that agenda doesn't already exist in the database
            if not self.agenda_exists(agenda_url):
                agenda_string = agenda.text.strip()

                # El Reno agenda names contain both date and title, or sometimes just date
                # Test if agenda title contains letters first
                agenda_date = ""
                agenda_name = self.name
                match = re.search('[a-zA-Z]', agenda_string)
                if match:
                    # If it does, then we must separate date from title
                    match = re.search(r'\d{1,2}-\d{1,2}-\d{1,4}', agenda_string)
                    if match:
                        agenda_date = self.create_date(agenda_string[match.start():match.end()])
                        agenda_name = agenda_string.replace(
                            agenda_string[match.start():match.end()], "").strip()
                    else:
                        # In some cases, agenda title doesn't contain any dates
                        # This is most likely the yearly council dates announcement
                        # In this case, set the date to Jan 1 of current year
                        agenda_date = self.create_date("1/1")
                        agenda_name = agenda_string
                else:
                    # Otherwise, agenda title is just the date
                    agenda_date = self.create_date(agenda_string)

                # If agenda is not older than cut-off date,
                # Store agenda information and append to agenda list
                if not self.too_old(agenda_date):
                    agenda = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_name,
                        "agenda_url": agenda_url,
                        "agenda_text": "", # will be generated upon user request
                        "pdf_link": agenda_url
                    }
                    agenda_list.append(agenda)

        return agenda_list
