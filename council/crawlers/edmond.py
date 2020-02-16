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
from datetime import datetime
import requests
import dateutil.parser as dparser
from django.utils.timezone import get_current_timezone
from bs4 import BeautifulSoup, SoupStrainer
from ..modules.crawler_helpers import agenda_exists, set_progress
from ..models import Agenda

def get_new_agendas(department, progress_recorder):
    """
    This method searches for new agendas for a given department and
    saves whatever new agendas it finds to the database. It performs
    a complete crawling operation that retrieves agendas, filters them
    accordindingly, formats the data into agenda objects, and then saves
    the new agenda objects to the datbase.
    """
    crawler_name = "Edmond"
    print("--- {} AGENDA CRAWLER ---".format(crawler_name.upper()))

    # Fetch agenda page as response object
    print("{}: Getting response object...".format(crawler_name))
    set_progress(progress_recorder, 0, 10, "Connecting to City website...", 2)
    response = requests.get(department.agendas_url, timeout=10)
    set_progress(progress_recorder, 1, 10, \
        "Connection succeeded. Getting current list of agendas...", 2)

    # Extract HTML using BeautifulSoup
    print("{}: Extracting HTML with BeautifulSoup...".format(crawler_name))
    agendas_table = SoupStrainer("tbody", class_="nowrap smallText")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=agendas_table)
    rows = soup.find_all("tr")
    status = "Searching list for any new {} agendas...".format(department.department_name)
    set_progress(progress_recorder, 2, 10, status, 2)

    # Cycle through agenda list to find any new department agendas
    # For any that are found, store them in a list for futher processing
    print("{}: Looking for new {} agendas...".format(crawler_name, department.department_name))
    agenda_list = []
    for row in rows:
        agenda_url = "http://agenda.edmondok.com:8085/{}".format(row.a["href"])
        agenda_date = dparser.parse(row.a.text, fuzzy=True)
        agenda_title = row.find_all("td")[1].text
        agenda = {
            "agenda_url": agenda_url,
            "agenda_date": agenda_date,
            "agenda_title": agenda_title
        }
        # Check to see if agenda matches the department
        # and doesn't already exist in the database
        if agenda.get("agenda_title").lower().strip() == \
            department.department_name.lower().strip():
            if not agenda_exists(agenda.get("agenda_url")):
                agenda_list.append(agenda)
    status = "Found {} new agenda(s).".format(len(agenda_list))
    print("{}: {}".format(crawler_name, status))
    set_progress(progress_recorder, 3, 10, status, 2)

    # For each new agenda, access its agenda detail page and extract the agenda HTML,
    # prepare it for saving to the database, and then save it to the database
    i = 1
    progress_step = 3
    progress_length = len(agenda_list)*2 + 4
    for agenda in agenda_list:
        # Update progress bar status and print
        status = "Getting contents of agenda {} of {}...".format(i, len(agenda_list))
        print("{}: {}".format(crawler_name, status))
        progress_step += 1
        set_progress(progress_recorder, progress_step, progress_length, status, 2)

        # Get agenda detail page and extract HTML
        print("Agenda: {}".format(agenda.get("agenda_url")))
        response = requests.get(agenda.get("agenda_url"))
        strainer = SoupStrainer("table", class_=" tableCollapsed")
        soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)

        # Separate head and body in order to strip out non-essential info
        # at beginning of each Edmond agenda
        header = soup.thead.find_all("tr")[len(soup.thead.find_all("tr"))-1].text.strip()
        body = soup.tbody

        # Edmond uses a table to display body of agenda. BS4 has trouble extracting tables.
        # The below loops over the tbody tag, and for reach row of the table, it joins the
        # text in each of the columns into one string, and then formats a new table to display
        # the text correctly
        rows = body.find_all("tr")
        strings = []
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
        # text together into the agenda_text var for saving to the database
        body = "".join(strings)
        agenda_text = "{}\n\n<table>{}</table>".format(header, body)

        # Find PDF link (if available) and save to variable
        pdf_link = ""
        if soup.find("a", title="Download PDF Packet"):
            pdf_path = soup.find("a", title="Download PDF Packet")['href']
            pdf_link = "http://agenda.edmondok.com:8085{}".format(pdf_path)

        # Update progress bar status and print
        status = "Saving agenda {} of {} to database...".format(i, len(agenda_list))
        print("{}: {}".format(crawler_name, status))
        progress_step += 1
        set_progress(progress_recorder, progress_step, progress_length, status, 2)

        # Assemble all extracted information and create an Agenda object
        new_agenda = Agenda(
            agenda_date=agenda.get("agenda_date"),
            agenda_title=agenda.get("agenda_title"),
            agenda_url=agenda.get("agenda_url"),
            agenda_text=agenda_text,
            pdf_link=pdf_link,
            date_added=datetime.now(tz=get_current_timezone()),
            department=department
        )

        # Save new agenda to the database
        new_agenda.save()
        i += 1
