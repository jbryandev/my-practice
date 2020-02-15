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
import re
import requests
import dateutil.parser as dparser
from bs4 import BeautifulSoup, SoupStrainer
from ..modules.crawler_helpers import agenda_exists, set_progress

def retrieve_agendas(department, progress_recorder):
    """ This function scrapes agenda info from the City website. """

    crawler_name = "Edmond"
    print("--- {} AGENDA CRAWLER ---".format(crawler_name.upper()))

    try:
        # Set intial progress bar state and message
        set_progress(progress_recorder, 0, 15, "Connecting to City website...", 2)

        # Fetch website as response object
        print("{}: Getting response object...".format(crawler_name))
        response = requests.get(department.agendas_url, timeout=10)
        set_progress(progress_recorder, 1, 15, \
            "Connection succeeded. Getting current list of agendas...", 2)

        # Extract HTML using BeautifulSoup
        print("{}: Extracting HTML with BeautifulSoup...".format(crawler_name))
        agendas_table = SoupStrainer("tbody", class_="nowrap smallText")
        soup = BeautifulSoup(response.text, "html.parser", parse_only=agendas_table)
        rows = soup.find_all("tr")
        status = "Searching list for any new {} agendas...".format(department.department_name)
        set_progress(progress_recorder, 2, 15, status, 2)

        # Cycle through agenda list to find any new department agendas
        # For any that are found, store them in a list for futher processing
        print("{}: Looking for new {} agendas...".format(crawler_name, department.department_name))
        agenda_list = []
        for row in rows:
            agenda_url = "http://agenda.edmondok.com:8085/{}".format(row.a["href"])
            agenda_date = dparser.parse(row.a.text, fuzzy=True)
            agenda_dept = row.find_all("td")[1].text
            agenda = {
                "agenda_url": agenda_url,
                "agenda_date": agenda_date,
                "agenda_dept": agenda_dept
            }
            # Check to see if agenda matches the department
            # and doesn't already exist in the database
            if agenda.get("agenda_dept").lower().strip() == \
                department.department_name.lower().strip():
                if not agenda_exists(agenda.get("agenda_url")):
                    agenda_list.append(agenda)
        status = "Found {} new agenda(s).".format(len(agenda_list))
        print(status)
        set_progress(progress_recorder, 3, 15, status, 2)

        # For each new agenda, access its agenda detail page and extract the agenda HTML
        i = 1
        for agenda in agenda_list:
            status = "Getting contents of agenda {} of {}...".format(i, len(agenda_list))
            print(status)
            set_progress(progress_recorder, i+4, len(agenda_list)+5, status, 2)
            response = requests.get(agenda_url)
            strainer = SoupStrainer("table", class_=" tableCollapsed")
            soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)
            header = soup.thead.find_all("tr")[len(soup.thead.find_all("tr"))-1].text.strip()
            body = soup.tbody
            rows = body.find_all("tr")
            string_list = []
            for row in rows:
                if "." in row.text:
                    col = row.find_all("td")
                    if not col[0].text.strip() and not col[1].text.strip() and col[2].text.strip():
                        string_list.append("<tr><td style=\"width: 10%\"></td><td style=\"width: 10%\"></td><td>{}</td></tr>".format(row.text.strip().replace('\n', '').replace('\xa0', '')))
                    elif not col[0].text.strip() and col[1].text.strip():
                        string_list.append("<tr><td style=\"width: 10%\"></td><td colspan=\"2\">{}</td></tr>".format(row.text.strip().replace('\n', '').replace('\xa0', '')))
                    elif col[0].text.strip():
                        string_list.append("<tr><td colspan=\"3\">{}</td></tr>".format(row.text.strip().replace('\n', '').replace('\xa0', '')))
            body_text = "".join(string_list)
            table_text = "<table class=\">{}</table>".format(body_text)
            i += 1

    except Exception as error:
        print(error)
        #set_progress() to error state and provide error message/code


def retrieve_current_agendas(agendas_url):
    """
    This function takes the URL where the agendas are located and returns
    a BeautifulSoup object with the parsed HTML
    """
    response = requests.get(agendas_url)
    # Don't need entire HTML page, just parse only TABLE tag containing the agendas
    agendas_table = SoupStrainer(class_="nowrap smallText")

    return BeautifulSoup(response.text, "html.parser", parse_only=agendas_table)

def find_specific_agendas(parsed_html, agenda_name):
    """
    This function takes a BeautifulSoup object containing parsed HTML and
    the agenda name to search for, and returns a list of matching agendas.
    The resulting list will contain key value pairs of the agenda date as
    a datetime object and the agenda URL as a string.
    """
    agenda_set = []
    for tag in parsed_html.find_all("td", string=re.compile("%s" % agenda_name)):
        # Select first child in tag, which contains all the agenda info we need
        agenda_info = tag.parent.td

        # Convert agenda date string into datetime object
        agenda_date = dparser.parse(agenda_info.text, fuzzy=True)

        # Check for existence of agenda link and create agenda object if exists
        if agenda_info.a:
            agenda_url = "http://agenda.edmondok.com:8085/" + agenda_info.a['href']
            agenda = {"agenda_date": agenda_date, "agenda_url": agenda_url}
            agenda_set.append(agenda)

    return agenda_set

def get_agenda(agenda_url):
    """ This function takes an agenda URL and extracts the agenda contents. """
    # Connect to the agenda URL and parse agenda HTML through BeautifulSoup
    response = requests.get(agenda_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find PDF link (if available) and save to variable
    download_link = soup.find("a", title="Download PDF Packet")
    agenda_pdf = ""
    if download_link:
        agenda_pdf = "http://agenda.edmondok.com:8085" + download_link['href']

    # Parse out agenda HTML and save as agenda text
    rows = soup.find_all("tr")
    agenda_text = ""
    i = 3
    while i < len(rows):
        agenda_text += (rows[i].text.strip() + "\n")
        i += 1

    agenda = {"agenda_url": agenda_url, "pdf_link": agenda_pdf, "agenda_text": agenda_text}

    return agenda
