""" Views for the application """
from django.shortcuts import get_object_or_404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from celery.result import AsyncResult
from .crawler import exec_crawler
from .modules import pdf2text
from .models import Agency, Department, Agenda, Crawler

# Create your views here.

class IndexView(generic.ListView):
    """ View for the index page of the application """
    template_name = 'council/index.html'

    def get_queryset(self):
        return Agency.objects.order_by('agency_name')

class AgencyView(generic.DetailView):
    """ View for the agency detail page """
    model = Agency
    template_name = 'council/agency_detail.html'

class DepartmentView(generic.DetailView):
    """ View for the department detail page """
    model = Department
    template_name = 'council/department_detail.html'

class AgendaView(generic.DetailView):
    """ View for the agenda detail page """
    model = Agenda
    template_name = 'council/agenda_detail.html'

def fetch_agendas(request, dept_id):
    """ Function to fetch new agendas for a department """
    department = get_object_or_404(Department, pk=dept_id)
    crawler = get_object_or_404(Crawler, department=department)
    exec_crawler(crawler, department)

    return HttpResponseRedirect(reverse('council:department-detail', args=[str(dept_id)]))

def convert_pdf(request, agenda_id):
    """ Function to convert a PDF agenda into text """
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda.agenda_text = pdf2text.convert_pdf.delay(agenda.agenda_url)
    agenda.save()

    return HttpResponseRedirect(reverse('council:agenda-detail', args=[str(agenda_id)]))

"""
def get_progress(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        'state': result.state,
        'details': result.info,
    }
    return HttpResponse(json.dumps(response_data), content_type='application/json')
"""