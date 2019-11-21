from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Agency, Department, Agenda

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

def FetchAgendas(request, pk):
    # Call fetch_agendas() function based on provided Department id
    department = Department.objects.get(id=pk)
    department.fetch_agendas()
    return HttpResponseRedirect(reverse('council:department-detail', args=[str(pk)]))