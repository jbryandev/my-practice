""" Views for the application """
from datetime import date, timedelta
from django.views import generic
from council.models import Agency, Department, Agenda
from council.tasks import convert_pdf_to_text, fetch_agendas, generate_highlights

# Create your views here.

class IndexView(generic.ListView):
    """ View for the index page of the application """
    template_name = 'council/index.html'

    def get_queryset(self):
        return Agency.objects.order_by('agency_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = date.today()
        start = current_date - timedelta(days=current_date.weekday())
        end = start + timedelta(days=4)
        this_weeks_agendas = Agenda.objects.filter(
            agenda_date__range=(start, end)).order_by('agenda_date')
        context['this_weeks_agendas'] = this_weeks_agendas
        return context

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
    template_name = 'council/department_detail.html'

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
        result = convert_pdf_to_text.delay(context['agenda'].pk)
        context['convert_task_id'] = result.task_id
        return context

class AgendaHighlightView(generic.DetailView):
    """ View for the agenda generate highlights page """
    model = Agenda
    template_name = 'council/agenda_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = generate_highlights.delay(context['agenda'].pk)
        context['highlight_task_id'] = result.task_id
        return context
