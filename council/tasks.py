""" Task Module for Celery """
from celery import shared_task
from django.shortcuts import get_object_or_404
from .crawler import exec_crawler
from .models import Agenda, Department, Crawler
from .modules.pdf2text import convert_pdf

@shared_task(bind=True)
def convert_to_pdf(self, agenda_id):
    """ Convert agenda to PDF in the background using celery """
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    agenda.agenda_text = convert_pdf(self, agenda_url)
    agenda.save()

    return "PDF conversion complete."

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    department = get_object_or_404(Department, pk=dept_id)
    crawler = get_object_or_404(Crawler, department=department)
    exec_crawler(crawler, department)

    return "Fetch agendas complete."
