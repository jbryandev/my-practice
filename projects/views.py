""" Views for Projects app """
from django.views import generic
from django_tables2 import SingleTableView
from .models import Project
from .tables import ProjectTable

class IndexView(SingleTableView):
    """ View for Projects index page """
    template_name = 'projects/index.html'
    table_class = ProjectTable
    def get_queryset(self):
        return Project.objects.order_by('project_name')

class DetailView(generic.DetailView):
    """ View for Projects detail page """
    model = Project
    template_name = 'projects/detail.html'
