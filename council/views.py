from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .models import Agency

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'council/index.html'
    def get_queryset(self):
        return Agency.objects.order_by('agency_name')
