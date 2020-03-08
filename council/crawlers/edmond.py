"""
Crawler for the City of Edmond. Edmond uses an online meeting agenda system,
and agendas are presented in HTML format with a link to download as a PDF.
This crawler will read the HTML agenda, since that will be more reliable
than using OCR to convert the PDF to text.

Since all agendas are posted to the online system, this crawler can be
used to handle any City department, as the extraction method will be
the same.

Edmond lists their agendas by month. Therefore, we don't need to worry about
extracting agendas older than the current month.
"""
from council.crawlers.crawler import Crawler
from council.modules.backend import set_progress

class EdmondCrawler(Crawler):

    def crawl(self, progress_recorder):
        # Request City agenda website
        set_progress(progress_recorder, 0, 10, "Connecting to City website...")
        response = self.get_url(self.url)

        # Extract HTML with BeautifulSoup
        set_progress(progress_recorder, 1, 10, \
            "Connection succeeded. Getting current list of agendas...", 2)
        strainer = self.get_strainer("tbody", class_="nowrap smallText")
        soup = self.get_soup(response, "html.parser", parse_only=strainer)

        # Search agenda list for any new department agendas
        status = "Searching list for any new {} agendas...".format(self.name)
        set_progress(progress_recorder, 2, 10, status, 2)
        agenda_list = self.get_agendas(soup)
        status = "Found {} new agenda(s).".format(len(agenda_list))
        set_progress(progress_recorder, 3, 10, status, 2)

        # Loop over any new agendas, extract the agenda info, and save to database
        i = 1
        progress_step = 3
        progress_length = len(agenda_list)*2 + 4
        for agenda in agenda_list:
            # Get contents of agenda
            status = "Getting contents of agenda {} of {}...".format(i, len(agenda_list))
            progress_step += 1
            set_progress(progress_recorder, progress_step, progress_length, status, 2)
            response = self.get_url(agenda.get("agenda_url"))
            strainer = self.get_strainer("table", class_=" tableCollapsed")
            soup = self.get_soup(response, "html.parser", parse_only=strainer)
            agenda_text = self.get_agenda_text(soup)
            pdf_link = self.get_pdf_link(soup)
            agenda.update({
                "agenda_text": agenda_text,
                "pdf_link": pdf_link
            })

            # Save agenda to database
            status = "Saving agenda {} of {} to the database...".format(i, len(agenda_list))
            progress_step += 1
            set_progress(progress_recorder, progress_step, progress_length, status, 2)
            new_agenda = self.create_new_agenda(agenda)
            new_agenda.save()
            i += 1

    def get_agendas(self, soup):
        agenda_list = []
        rows = soup.find_all("tr")
        for row in rows:
            agenda_url = "http://agenda.edmondok.com:8085/{}".format(row.a["href"])
            agenda_date = self.create_date(row.a.text)
            agenda_title = row.find_all("td")[1].text
            # Check to see if agenda matches the department
            if agenda_title.lower().strip() == self.name.lower().strip():
                # and doesn't already exist in the database
                if not self.agenda_exists(agenda_url):
                    agenda = {
                        "agenda_url": agenda_url,
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title
                    }
                    agenda_list.append(agenda)

        return agenda_list

    def get_agenda_text(self, soup):
        # Separate head and body in order to strip out non-essential info
        # at beginning of each Edmond agenda
        header = soup.thead.find_all("tr")[len(soup.thead.find_all("tr"))-1].text.strip()
        body = soup.tbody
        rows = body.find_all("tr")
        strings = []
        # Edmond uses a table to display body of agenda. BS4 has trouble extracting tables.
        # The code below loops over the tbody tag, and for each row of the table, it joins the
        # text in each of the columns into one string, and then creates a new table to display
        # the text correctly
        for row in rows:
            if "." in row.text:
                col = row.find_all("td")
                if not col[0].text.strip() and not col[1].text.strip() and col[2].text.strip():
                    strings.append("<tr><td style=\"width: 10%\"></td><td style=\"width: \
                        10%\"></td><td>{}\n\n</td></tr>".format(row.text.strip().\
                        replace('\n', '').replace('\xa0', '')))
                elif not col[0].text.strip() and col[1].text.strip():
                    strings.append("<tr><td style=\"width: 10%\"></td><td \
                        colspan=\"2\">{}\n\n</td></tr>".format(row.text.strip().\
                        replace('\n', '').replace('\xa0', '')))
                elif col[0].text.strip():
                    strings.append("<tr><td colspan=\"3\">{}\n\n</td></tr>".\
                        format(row.text.strip().replace('\n', '').replace('\xa0', '')))
        # Join the rows of body text together into one string, and then put the header and body
        # text together to create agenda_text
        body = "".join(strings)
        agenda_text = "{}\n\n<table>{}</table>".format(header, body)

        return agenda_text

    def get_pdf_link(self, soup):
        if soup.find("a", title="Download PDF Packet"):
            pdf_path = soup.find("a", title="Download PDF Packet")['href']
            pdf_link = "http://agenda.edmondok.com:8085{}".format(pdf_path)
            return pdf_link
        else:
            return ""
