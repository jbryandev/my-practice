from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import get_current_timezone
from django.views import generic
from datetime import datetime

from .models import Agency, Department, Agenda, Crawler
from .crawlers.controller import exec_crawler

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

