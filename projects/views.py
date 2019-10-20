from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Project

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'projects/index.html'

    def get_queryset(self):
        return Project.objects.order_by('-start_date')

class DetailView(generic.DetailView):
    model = Project
    template_name = 'projects/detail.html'