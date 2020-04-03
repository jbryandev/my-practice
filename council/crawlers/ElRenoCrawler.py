import re
from .Crawler import Crawler

class ElRenoCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("div", class_="javelin_regionContent")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        # Current year agendas SHOULD be found at soup.contents[1].contents[3]
        # This is the first group of agendas at the top of the agenda page
        current_year_agendas = parsed_html.contents[1].contents[3].find_all("li")

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
                    filtered_agendas.append(agenda)
        return filtered_agendas

    def parse_agenda(self, agenda):
        # This function is not needed for this crawler
        # It simply returns the input
        return agenda
