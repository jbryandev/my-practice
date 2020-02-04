"""
This is a controller linking Crawler objects and their
corresponding crawler modules. The controller creates
new Agenda objects and adds them to the database.
"""
import time
from datetime import datetime
from django.utils.timezone import get_current_timezone
from .crawlers import edmond
from .crawlers import el_reno
from .crawlers import lawton
from .crawlers import midwest_city
from .crawlers import moore
from .crawlers import norman
from .crawlers import okc
from .crawlers import tulsa
from .models import Agenda

def agenda_exists(agenda_url):
    """
    This function takes an agenda URL and makes sure that it is not
    already associated with an agenda in the database.
    """
    return bool(Agenda.objects.filter(agenda_url=agenda_url).exists())

def set_progress(progress_recorder, start, end, descr, delay):
    """ This function controls the progress recorder """
    progress_recorder.set_progress(start, end, description=descr)
    time.sleep(delay)

def exec_crawler(crawler, calling_department, progress_recorder):
    """ Linking function between Crawler models and Crawler modules. """

    if crawler.crawler_name == "Edmond":
        edmond_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "El Reno":
        el_reno_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Lawton":
        lawton_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Midwest City":
        midwest_city_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Moore":
        moore_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Oklahoma City":
        okc_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Norman":
        norman_crawler(calling_department, progress_recorder)

    elif crawler.crawler_name == "Tulsa":
        tulsa_crawler(calling_department, progress_recorder)

def edmond_crawler(calling_department, progress_recorder):
    """ Edmond Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url
    agenda_name = calling_department.department_name

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agenda_html = edmond.retrieve_current_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for department-specific agendas...")
    time.sleep(2)
    specific_agendas = edmond.find_specific_agendas(agenda_html, agenda_name)

    if specific_agendas:
        progress_desc = "Found " + str(len(specific_agendas)) + " department agendas."
        progress_recorder.set_progress(3, 15, description=progress_desc)
        time.sleep(2)

        i = 1
        j = 0

        for agenda in specific_agendas:
            progress_desc = "Processing agenda " + str(i) + " of " \
                + str(len(specific_agendas)) + "..."
            progress_recorder.set_progress(i+3, len(specific_agendas)+4, description=progress_desc)
            time.sleep(1)
            agenda_url = agenda.get("agenda_url")
            if not agenda_exists(agenda_url):
                j += 1
                parsed_agenda = edmond.get_agenda(agenda_url)
                parsed_agenda.update(
                    {
                        "agenda_date": agenda.get("agenda_date"),
                        "agenda_name": agenda_name
                    }
                )
                new_agenda = Agenda(
                    agenda_date=parsed_agenda.get("agenda_date"),
                    agenda_title=parsed_agenda.get("agenda_name"),
                    agenda_url=parsed_agenda.get("agenda_url"),
                    agenda_text=parsed_agenda.get("agenda_text"),
                    pdf_link=parsed_agenda.get("pdf_link"),
                    date_added=datetime.now(tz=get_current_timezone()),
                    department=calling_department
                )
                new_agenda.save()
            i += 1
        progress_desc = "Finished processing. Found " + str(j) + " new agendas."
        progress_recorder.set_progress(14, 15, description=progress_desc)
        time.sleep(2)
    else:
        progress_recorder.set_progress(
            14, 15, description="Did not find any matching department agendas.")
        time.sleep(2)

def el_reno_crawler(calling_department, progress_recorder):
    """ El Reno Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = el_reno.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Selecting most recent agendas...")
    time.sleep(2)
    recent_agendas = el_reno.get_most_recent_agendas(agendas_list)

    i = 1
    j = 0

    for agenda in recent_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(recent_agendas)) + "..."
        progress_recorder.set_progress(i+3, len(recent_agendas)+4, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.a["href"]

        if not agenda_exists(agenda_url):
            j += 1
            parsed_agenda = el_reno.parse_agenda_info(agenda)
            new_agenda = Agenda(
                agenda_date=parsed_agenda.get("agenda_date"),
                agenda_title=parsed_agenda.get("agenda_title"),
                agenda_url=parsed_agenda.get("agenda_url"),
                agenda_text=parsed_agenda.get("agenda_text"),
                pdf_link=parsed_agenda.get("pdf_link"),
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(5)

def lawton_crawler(calling_department, progress_recorder):
    """ Lawton Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = lawton.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = lawton.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = lawton.get_agenda_url(agenda.get("agenda_detail_url"))

        if not agenda_exists(agenda_url):
            j += 1
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text="", # will be generated upon user request
                pdf_link=agenda_url,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def midwest_city_crawler(calling_department, progress_recorder):
    """ Edmond Crawler function. """
    descr = 'Connecting to City website...'
    set_progress(progress_recorder, 0, 15, descr, 2)
    agendas_url = calling_department.agendas_url

    descr = 'Connection succeeded. Getting agenda list...'
    set_progress(progress_recorder, 1, 15, descr, 2)
    agendas_list = midwest_city.retrieve_agendas(agendas_url)

    descr = 'Searching for matching department agendas...'
    set_progress(progress_recorder, 2, 15, descr, 2)
    matched_agendas = midwest_city.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        total = len(matched_agendas)
        descr = "Processing agenda " + str(i) + " of " + str(total) + "..."
        set_progress(progress_recorder, i+2, total+3, descr, 1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text="", # will be generated upon user request
                pdf_link=agenda_url,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    descr = "Finished processing. Found " + str(j) + " new agendas."
    set_progress(progress_recorder, 14, 15, descr, 2)

def moore_crawler(calling_department, progress_recorder):
    """ Moore Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = moore.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = moore.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = moore.get_agenda_url(agenda.get("agenda_detail"))

        if agenda_url:
            if not agenda_exists(agenda_url):
                j += 1
                new_agenda = Agenda(
                    agenda_date=agenda.get("agenda_date"),
                    agenda_title=agenda.get("agenda_title"),
                    agenda_url=agenda_url,
                    agenda_text="", # will be generate upon user request
                    pdf_link=agenda_url,
                    date_added=datetime.now(tz=get_current_timezone()),
                    department=calling_department
                )
                new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def norman_crawler(calling_department, progress_recorder):
    """ Norman Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = norman.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = norman.match_agendas(agendas_list, calling_department.department_name)

    i = 0
    j = 1

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text="", # will be generated upon user request
                pdf_link=agenda_url,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def okc_crawler(calling_department, progress_recorder):
    """ OKC Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = okc.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = okc.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")
        agenda_view_link = agenda.get("agenda_view_link")

        if not agenda_exists(agenda_url):
            j += 1
            agenda_text = okc.get_agenda_text(agenda_url)
            pdf_link = okc.get_agenda_pdf(agenda_view_link)
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text=agenda_text,
                pdf_link=pdf_link,
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)

def tulsa_crawler(calling_department, progress_recorder):
    """ Tulsa Crawler function. """
    progress_recorder.set_progress(0, 15, description="Connecting to City website...")
    time.sleep(2)
    agendas_url = calling_department.agendas_url

    progress_recorder.set_progress(
        1, 15, description="Connection succeeded. Getting agenda list...")
    time.sleep(2)
    agendas_list = tulsa.retrieve_agendas(agendas_url)

    progress_recorder.set_progress(
        2, 15, description="Searching for matching department agendas...")
    time.sleep(2)
    matched_agendas = tulsa.match_agendas(agendas_list, calling_department.department_name)

    i = 1
    j = 0

    for agenda in matched_agendas:
        progress_desc = "Processing agenda " + str(i) + " of " + str(len(matched_agendas)) + "..."
        progress_recorder.set_progress(i+2, len(matched_agendas)+3, description=progress_desc)
        time.sleep(1)
        agenda_url = agenda.get("agenda_url")

        if not agenda_exists(agenda_url):
            j += 1
            agenda_text = tulsa.get_agenda_content(agenda_url)
            new_agenda = Agenda(
                agenda_date=agenda.get("agenda_date"),
                agenda_title=agenda.get("agenda_title"),
                agenda_url=agenda_url,
                agenda_text=agenda_text,
                pdf_link="",
                date_added=datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()
        i += 1

    progress_desc = "Finished processing. Found " + str(j) + " new agendas."
    progress_recorder.set_progress(14, 15, description=progress_desc)
    time.sleep(2)
