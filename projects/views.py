from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django_tables2 import SingleTableView

from .models import Project
from .tables import ProjectTable

# Create your views here.

class IndexView(SingleTableView):
    template_name = 'projects/index.html'
    table_class = ProjectTable
    def get_queryset(self):
        return Project.objects.order_by('project_name')

class DetailView(generic.DetailView):
    model = Project
    template_name = 'projects/detail.html'