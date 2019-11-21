from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages

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

    department = Department.objects.get(id=pk)
    crawler = None
    try:
        crawler = Crawler.objects.get(department=department)
    except:
        messages.error(request, 'Error: There isn\'t a crawler assigned to this department yet.')

    if crawler:
        try:
            exec_crawler(request, crawler, department)
        except:
            #messages.error(request, 'Unable to locate corresponding crawler module')
            pass

    return HttpResponseRedirect(reverse('council:department-detail', args=[str(pk)]))

def exec_crawler(request, crawler, calling_department):
    # Linking function between Crawler models and Crawler modules
    
    if crawler.crawler_name == "Edmond":
        module = importlib.import_module("council.crawlers.edmond")
        agendas_url = calling_department.agendas_url
        agenda_name = calling_department.department_name
        new_agendas = module.fetch_agendas(agendas_url, agenda_name)
        module.save_agendas(new_agendas, calling_department)
        return True
    
    elif crawler.crawler_name == "El Reno":
        module = importlib.import_module("council.crawlers.el_reno")
        agendas_url = calling_department.agendas_url
        new_agendas = module.fetch_agendas(agendas_url)
        module.save_agendas(new_agendas, calling_department)