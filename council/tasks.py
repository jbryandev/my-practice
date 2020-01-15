""" Task Module for Celery """
import time
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.shortcuts import get_object_or_404
from .crawler import exec_crawler
from .models import Agenda, Department, Crawler
from .modules.pdf2text import convert_pdf

@shared_task(bind=True)
def convert_to_pdf(self, agenda_id):
    """ Convert agenda to PDF in the background using celery """
    progress_recorder = ProgressRecorder(self)
    progress_recorder.set_progress(0, 15, description="Attempting to connect...")
    agenda = Agenda.objects.get(pk=agenda_id)
    agenda_url = agenda.agenda_url
    agenda.agenda_text = convert_pdf(agenda_url, progress_recorder)
    progress_recorder.set_progress(
        14, 15, description="PDF conversion complete. Saving to database...")
    time.sleep(2)
    agenda.save()

    return "PDF conversion complete."

@shared_task(bind=True)
def fetch_agendas(self, dept_id):
    """ Fetch new agendas for a given department via celery """
    department = get_object_or_404(Department, pk=dept_id)
    crawler = get_object_or_404(Crawler, department=department)
    exec_crawler(crawler, department)

    return "Fetch agendas complete."
