""" Views for the application """
#from django.shortcuts import get_object_or_404, HttpResponseRedirect
#from django.urls import reverse
from django.views import generic
#from .crawler import exec_crawler
from .models import Agency, Department, Agenda
from .tasks import convert_to_pdf, fetch_agendas

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

class DepartmentFetchView(generic.DetailView):
    """ View for the department fetch agendas page """
    model = Department
    template_name = 'council/department_fetch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = fetch_agendas.delay(context['department'].pk)
        context['task_id'] = result.task_id
        return context

class AgendaView(generic.DetailView):
    """ View for the agenda detail page """
    model = Agenda
    template_name = 'council/agenda_detail.html'

    def get(self, request, *args, **kwargs):
        """ On page get, set viewed attribute to true """
        agenda = Agenda.objects.get(pk=self.get_object().id)
        agenda.viewed = True
        agenda.save()
        return super(AgendaView, self).get(request, *args, **kwargs)

class AgendaConvertView(generic.DetailView):
    """ View for the agenda convert  page """
    model = Agenda
    template_name = 'council/agenda_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = convert_to_pdf.delay(context['agenda'].pk)
        context['task_id'] = result.task_id
        return context
