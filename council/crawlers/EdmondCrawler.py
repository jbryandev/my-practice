from council.crawlers.Crawler import Crawler

class EdmondCrawler(Crawler):

    def __init__(self, department, progress_recorder):
        super().__init__(department, progress_recorder)
        self.set_strainer("tbody", class_="nowrap smallText")

    def filter_agendas(self, parsed_html):
        filtered_agendas = []
        rows = parsed_html.find_all("tr")
        for row in rows:
            agenda_url = "http://agenda.edmondok.com:8085/{}".format(row.a["href"])
            agenda_date = self.create_date(row.a.text)
            agenda_title = row.find_all("td")[1].text
            # Check to see if agenda matches the department
            if agenda_title.lower().strip() == self.name.lower().strip():
                # and doesn't already exist in the database
                if not self.agenda_exists(agenda_url):
                    agenda = {
                        "agenda_date": agenda_date,
                        "agenda_title": agenda_title,
                        "agenda_url": agenda_url,
                    }
                    filtered_agendas.append(agenda)
        return filtered_agendas

    def parse_agenda(self, agenda):
        response = self.request(agenda.get("agenda_url"))
        self.set_strainer("table", class_=" tableCollapsed")
        soup = self.get_soup(response.text, "html.parser", parse_only=self.strainer)
        agenda_text = self.get_agenda_text(soup)
        pdf_link = self.get_pdf_link(soup)
        agenda.update({
            "agenda_text": agenda_text,
            "pdf_link": pdf_link
        })
        return agenda

    @staticmethod
    def get_agenda_text(soup):
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

    @staticmethod
    def get_pdf_link(soup):
        if soup.find("a", title="Download PDF Packet"):
            pdf_path = soup.find("a", title="Download PDF Packet")['href']
            pdf_link = "http://agenda.edmondok.com:8085{}".format(pdf_path)
            return pdf_link
        return ""
