from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import get_current_timezone
from django.views import generic
from datetime import datetime
import importlib

from .models import Agency, Department, Agenda, Crawler

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'council/index.html'
    
    def get_queryset(self):
        return Agency.objects.order_by('agency_name')

class AgencyView(generic.DetailView):
    model = Agency
    template_name = 'council/agency_detail.html'

class DepartmentView(generic.DetailView):
    model = Department
    template_name = 'council/department_detail.html'

class AgendaView(generic.DetailView):
    model = Agenda
    template_name = 'council/agenda_detail.html'

def fetch_agendas(request, pk):

    department = get_object_or_404(Department, pk=pk)
    crawler = get_object_or_404(Crawler, department=department)
    exec_crawler(crawler, department)
    
    return HttpResponseRedirect(reverse('council:department-detail', args=[str(pk)]))

def exec_crawler(crawler, calling_department):
    # Linking function between Crawler models and Crawler modules
    
    if crawler.crawler_name == "Edmond":
        edmond_crawler(calling_department)
    
    elif crawler.crawler_name == "El Reno":
        el_reno_crawler(calling_department)

def agenda_exists(agenda_url):
    # This function takes an agenda URL and makes sure that it is not
    # already associated with an agenda in the database
    if Agenda.objects.filter(agenda_url=agenda_url).exists():
        return True
    else:
        return False

def edmond_crawler(calling_department):
    module = importlib.import_module("council.crawlers.edmond")
    agendas_url = calling_department.agendas_url
    agenda_name = calling_department.department_name
    agenda_html = module.retrieve_current_agendas(agendas_url)
    specific_agendas = module.find_specific_agendas(agenda_html, agenda_name)
    for agenda in specific_agendas:
        agenda_url = agenda.get("agenda_url")
        if not agenda_exists(agenda_url):
            parsed_agenda = module.get_agenda(agenda_url)
            parsed_agenda.update({"agenda_date": agenda.get("agenda_date"), "agenda_name": agenda_name})
            new_agenda = Agenda(
                agenda_date=parsed_agenda.get("agenda_date"),
                agenda_title=parsed_agenda.get("agenda_name"),
                agenda_url=parsed_agenda.get("agenda_url"),
                agenda_text=parsed_agenda.get("agenda_text"),
                pdf_link=parsed_agenda.get("pdf_link"),
                date_added = datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()

def el_reno_crawler(calling_department):
    module = importlib.import_module("council.crawlers.el_reno")
    agendas_url = calling_department.agendas_url
    agendas_list = module.retrieve_agendas(agendas_url)
    recent_agendas = module.get_most_recent_agendas(agendas_list)
    for agenda in recent_agendas:
        agenda_url = agenda.a["href"]
        if not Agenda.objects.filter(agenda_url=agenda_url).exists():
            parsed_agenda = module.parse_agenda_info(agenda)
            new_agenda = Agenda(
                agenda_date=parsed_agenda.get("agenda_date"),
                agenda_title=parsed_agenda.get("agenda_title"),
                agenda_url=parsed_agenda.get("agenda_url"),
                agenda_text=parsed_agenda.get("agenda_text"),
                pdf_link=parsed_agenda.get("pdf_link"),
                date_added = datetime.now(tz=get_current_timezone()),
                department=calling_department
            )
            new_agenda.save()