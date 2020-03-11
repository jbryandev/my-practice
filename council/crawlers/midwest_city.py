"""
Crawler for the City of Midwest City. MC agendas are in PDF format, so this
crawler will use OCR to convert them to text.

Since all agendas are posted to the same main location, this crawler can
be used to handle any City department.
"""
import re
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class MidwestCityCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("table", id="table14")
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
        rows = soup.find_all("tr", limit=5)
        for agenda in rows:
            if agenda.p:
                agenda_string = agenda.p.text
                match = re.search(r'\d{4}', agenda_string)
                agenda_date = self.create_date(agenda_string[0:match.end()])
                # Make sure agenda isn't older than the cutoff date
                if not self.too_old(agenda_date):
                    agenda_title = agenda_string.replace(agenda_string[0:match.end()], "").strip()
                    # Check to see if agenda matches the department
                    if re.search(self.name.lower().strip(), agenda_title.lower().strip()):
                        agenda_url = "https://midwestcityok.org{}".format(agenda.find_all("a")[2]["href"])
                        # and doesn't already exist in the database
                        if not self.agenda_exists(agenda_url):
                            agenda = {
                                "agenda_date": agenda_date,
                                "agenda_title": agenda_title,
                                "agenda_url": agenda_url,
                                "agenda_text": "", # will be generated upon user request
                                "pdf_link": agenda_url
                            }
                            agenda_list.append(agenda)

        return agenda_list


# def retrieve_agendas(agendas_url):
#     """
#     This function takes a URL and retrieves all of the agendas
#     at this location. It returns a list of agenda objects.
#     """
#     response = requests.get(agendas_url)
#     agenda_tag = SoupStrainer("table", id="table14")
#     soup = BeautifulSoup(response.text, "html.parser", parse_only=agenda_tag)
#     rows = soup.find_all("tr", limit=6)
#     agenda_list = []
#     for agenda in rows:
#         if agenda.p:
#             agenda_string = agenda.p.text
#             match = re.search(r'\d{4}', agenda_string)
#             agenda_date = dparser.parse(agenda_string[0:match.end()], fuzzy=True)
#             agenda_name = agenda_string.replace(agenda_string[0:match.end()], "").strip()
#             agenda_url = "https://midwestcityok.org" + agenda.find_all("a")[2]["href"]
#             agenda_obj = {
#                 "agenda_date": agenda_date,
#                 "agenda_title": agenda_name,
#                 "agenda_url": agenda_url
#             }
#             agenda_list.append(agenda_obj)

#     return agenda_list

# def match_agendas(agenda_list, department_name):
#     """
#     This function takes a list of agendas, as well as the department name
#     to search for, and returns a list of agendas for the department.
#     """
#     matched_agendas = []
#     for agenda in agenda_list:
#         if re.search(department_name, agenda.get("agenda_title")):
#             matched_agendas.append(agenda)

#     return matched_agendas
