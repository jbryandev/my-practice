from datetime import datetime
from django.utils.timezone import get_current_timezone
from ..crawlers import edmond
from ..crawlers import el_reno
from ..crawlers import okc

from ..models import Agenda, Department

def exec_crawler(crawler, calling_department):
    # Linking function between Crawler models and Crawler modules
    
    if crawler.crawler_name == "Edmond":
        edmond_crawler(calling_department)
    
    elif crawler.crawler_name == "El Reno":
        el_reno_crawler(calling_department)

    elif crawler.crawler_name == "Oklahoma City":
        okc_crawler(calling_department)

def agenda_exists(agenda_url):
    # This function takes an agenda URL and makes sure that it is not
    # already associated with an agenda in the database
    if Agenda.objects.filter(agenda_url=agenda_url).exists():
        return True
    else:
        return False

def edmond_crawler(calling_department):
    agendas_url = calling_department.agendas_url
    agenda_name = calling_department.department_name
    agenda_html = edmond.retrieve_current_agendas(agendas_url)
    specific_agendas = edmond.find_specific_agendas(agenda_html, agenda_name)
    for agenda in specific_agendas:
        agenda_url = agenda.get("agenda_url")
        if not agenda_exists(agenda_url):
            parsed_agenda = edmond.get_agenda(agenda_url)
            parsed_agenda.update({"agenda_date": agenda.get("agenda_date"), "agenda_name": agenda_name})
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

def el_reno_crawler(calling_department):
    agendas_url = calling_department.agendas_url
    agendas_list = el_reno.retrieve_agendas(agendas_url)
    recent_agendas = el_reno.get_most_recent_agendas(agendas_list)
    for agenda in recent_agendas:
        agenda_url = agenda.a["href"]
        if not agenda_exists(agenda_url):
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

def okc_crawler(calling_department):
    agendas_url = calling_department.agendas_url
    agendas_list = okc.retrieve_agendas(agendas_url)
    matched_agendas = okc.match_agendas(agendas_list, calling_department.department_name)
    for agenda in matched_agendas:
        agenda_url = agenda.get("agenda_url")
        agenda_view_link = agenda.get("agenda_view_link")
        if not agenda_exists(agenda_url):
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